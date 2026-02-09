#!/usr/bin/env python3

import argparse
import os
import warnings

import numpy as np
import pandas as pd
import pydicom
import pylibjpeg
import segmentation as seg
from PIL import Image
from pydicom.pixel_data_handlers.util import convert_color_space
from tqdm import tqdm

warnings.filterwarnings("ignore", message="Invalid value for VR UI*")


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", required=True, help="Root directory")
    parser.add_argument(
        "--segmentation-subdir",
        default="retinal_octa/segmentation/topcon_maestro2",
        help="Segmentation folder relative to base_dir",
    )
    parser.add_argument(
        "--manifest-relpath",
        default="retinal_octa/manifest.tsv",
        help="Manifest TSV relative to base_dir",
    )
    parser.add_argument(
        "--out-filename",
        default="retinal_layer_thickness.csv",
        help="Output CSV filename",
    )
    args = parser.parse_args()

    base_dir = args.base_dir
    base_dir = os.path.join(args.base_dir, "dataset")
    output_dir = os.path.join(args.base_dir, "formatted_dataset")
    ensure_dir(output_dir)

    # --- Normalize paths ---
    seg_subdir = args.segmentation_subdir
    seg_subdir_pairing = seg_subdir if seg_subdir.startswith("/") else "/" + seg_subdir

    segmentation_abs = os.path.join(base_dir, seg_subdir.lstrip("/"))
    manifest_path = os.path.join(base_dir, args.manifest_relpath.lstrip("/"))

    print("base_dir:", base_dir)
    print("seg_subdir_pairing:", seg_subdir_pairing)
    print("segmentation_abs:", segmentation_abs)
    print("manifest_path:", manifest_path)

    if not os.path.isdir(segmentation_abs):
        raise FileNotFoundError(f"Segmentation directory not found: {segmentation_abs}")

    if not os.path.isfile(manifest_path):
        raise FileNotFoundError(f"Manifest TSV not found: {manifest_path}")

    # --- Get segmentation → OCT pairs ---
    seg_to_oct_dict = seg.get_seg_oct_pairs(base_dir, seg_subdir_pairing, manifest_path)
    print(f"Found {len(seg_to_oct_dict)} segmentation→OCT pairs")

    if len(seg_to_oct_dict) == 0:
        print("No matched pairs found. Check segmentation path and manifest.")
        return

    # --- Process each pair ---
    all_rows = []
    for seg_file, oct_file in tqdm(
        seg_to_oct_dict.items(), desc="Processing pairs", total=len(seg_to_oct_dict)
    ):
        try:
            row_df = seg.layer_thickness_etdrs_total_avg(seg_file, oct_file)
            all_rows.append(row_df)
        except Exception as e:
            print(f"Failed for: {seg_file}\n   OCT: {oct_file}\n   Reason: {e}")

    if not all_rows:
        print("No valid results to save.")
        return

    df = pd.concat(all_rows, ignore_index=True)
    print("Raw combined shape:", df.shape)

    # --- IQR filter numeric columns ---
    num_cols = [
        c
        for c in df.select_dtypes(include="number").columns
        if c not in ["Patient_ID", "Laterality"]
    ]
    if num_cols:
        df = seg.iqr_filter(df, num_cols)

    # --- Average per eye ---
    averaged_per_eye_df = (
        df.groupby(["Patient_ID", "Laterality"]).mean(numeric_only=True).reset_index()
    )
    print("Averaged per eye:", averaged_per_eye_df.shape)

    # --- Average across eyes per patient ---
    patient_avg_df = (
        averaged_per_eye_df.groupby("Patient_ID").mean(numeric_only=True).reset_index()
    )
    patient_avg_df["Laterality"] = "average"

    final_df = pd.concat([averaged_per_eye_df, patient_avg_df], ignore_index=True)
    final_df = final_df.sort_values(by=["Patient_ID", "Laterality"])

    # --- Map laterality ---
    laterality_map = {"R": "od", "L": "os"}
    final_df["Laterality"] = (
        final_df["Laterality"].map(laterality_map).fillna(final_df["Laterality"])
    )

    # --- Rename columns ---
    column_mapping = {
        "Thickness_ILM_to_RNFL/GCL": "retinal_nerve_fiber_layer_rnfl",
        "Thickness_RNFL/GCL_to_GCL": "ganglion_cell_layer_gcl",
        "Thickness_GCL_to_IPL/INL": "inner_plexiform_layer_ipl",
        "Thickness_IPL/INL_to_OPL": "inner_nuclear_layer_inl",
        "Thickness_OPL_to_ELM": "outer_nuclear_layer_onl",
        "Thickness_ELM_to_IS/OS": "photoreceptor_inner_segments_is",
        "Thickness_IS/OS_to_OS/RPE": "photoreceptor_outer_segments_os",
        "Thickness_OS/RPE_to_BM": "retinal_pigment_epithelium_rpe",
        "Patient_ID": "person_id",
        "Laterality": "laterality",
    }
    df = final_df.rename(columns=column_mapping)

    # --- Long → wide per person ---
    id_vars = ["person_id", "laterality"]
    layer_vars = [c for c in df.columns if c not in id_vars]

    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=layer_vars,
        var_name="layer",
        value_name="thickness",
    )
    df_long["layer_laterality"] = df_long["layer"] + "_" + df_long["laterality"]

    df_final = df_long.pivot(
        index="person_id", columns="layer_laterality", values="thickness"
    ).reset_index()

    df_final.columns.name = None
    print("Final wide shape:", df_final.shape)

    # --- Convert to micrometers ---
    cols_to_modify = [
        c
        for c in df_final.columns
        if c != "person_id" and pd.api.types.is_numeric_dtype(df_final[c])
    ]
    for c in cols_to_modify:
        df_final[c] = df_final[c] * 1000

    rename_map = {c: f"{c}_micrometer" for c in cols_to_modify}
    df_modified = df_final.rename(columns=rename_map)

    # --- Save ---
    out_csv = os.path.join(output_dir, args.out_filename)
    df_modified.to_csv(out_csv, index=False)
    print(f"Saved CSV to: {out_csv}")
    print("Final shape:", df_modified.shape)


if __name__ == "__main__":
    main()
