import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pydicom
from PIL import Image
from pydicom.pixel_data_handlers.util import convert_color_space
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pydicom
from PIL import Image


def get_seg_oct_pairs(base_dir, segmentation, table):
    # Load the manifest table
    df = pd.read_csv(table, sep="\t")

    seg_to_oct_dict = {}

    # Walk through directory and collect .dcm files
    for root, dirs, files in os.walk(base_dir + segmentation):
        for file in files:
            if file.endswith(".dcm"):
                full_path = os.path.join(root, file)
                relative_path = full_path.split(base_dir)[-1]

                # Find matching row in the manifest
                matching_row = df[
                    df["associated_segmentation_file_path"] == relative_path
                ]
                if not matching_row.empty:
                    oct_path = (
                        base_dir
                        + matching_row["associated_structural_oct_file_path"].values[0]
                    )
                    seg_to_oct_dict[full_path] = oct_path

    sorted_items = sorted(seg_to_oct_dict.items())
    ordered_dict = dict(sorted_items)

    print(f"Total matched pairs (sorted alphabetically): {len(ordered_dict)}")
    return ordered_dict


color_names = {
    (255, 0, 0): "Red",
    (0, 255, 0): "Green",
    (0, 0, 255): "Blue",
    (255, 255, 0): "Yellow",
    (0, 255, 255): "Cyan",
    (255, 0, 255): "Magenta",
    (255, 165, 0): "Orange",
    (128, 0, 128): "Purple",
    (255, 192, 203): "Pink",
    (165, 42, 42): "Brown",
}


def visualize_segmentation_by_layer(seg_file, oct_file, slice_index=160):
    """
    Visualizes an OCT b-scan with each segmented boundary drawn in a different
    color and displays a legend mapping colors to layer names.
    """
    oct_dcm = pydicom.dcmread(oct_file)
    seg_dcm = pydicom.dcmread(seg_file)

    oct_pixel_data = oct_dcm.pixel_array
    seg_pixel_data = seg_dcm.pixel_array

    ###

    seg_dcm = pydicom.dcmread(seg_file)

    # Map segment number -> label (safer than assuming order)
    segnum_to_label = {
        int(s.SegmentNumber): s.SegmentLabel for s in seg_dcm.SegmentSequence
    }

    pairs = []

    for i in range(len(seg_dcm.PerFrameFunctionalGroupsSequence)):
        fg = seg_dcm.PerFrameFunctionalGroupsSequence[i]

        instack_number = int(fg.FrameContentSequence[0].InStackPositionNumber)

        segment_number = int(
            fg.SegmentIdentificationSequence[0].ReferencedSegmentNumber
        )

        segment_label = segnum_to_label.get(segment_number, "UNKNOWN")

        pairs.append((instack_number, segment_label))

    # Sort by InStackPositionNumber
    pairs_sorted = sorted(pairs, key=lambda x: x[0])

    # Extract just the labels in stack order
    layer_boundary_names = [label for _, label in pairs_sorted]

    # 2. Create a color palette for the boundaries
    colors = [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (255, 255, 0),  # Yellow
        (0, 255, 255),  # Cyan
        (255, 0, 255),  # Magenta
        (255, 165, 0),  # Orange
        (128, 0, 128),  # Purple
        (255, 192, 203),  # Pink
        (165, 42, 42),  # Brown
    ]

    # Prepare the OCT b-scan for color overlay
    bscan = np.stack([oct_pixel_data[slice_index]] * 3, axis=2)

    # 3. Draw each boundary with a different color
    for j in range(seg_pixel_data.shape[0]):
        color = colors[j % len(colors)]  # Cycle through colors if needed
        cname = color_names.get(color, str(color))

        for zi, z in enumerate(seg_pixel_data[j, slice_index, :]):
            if z >= 0:
                z = round(z)
                if 0 <= z < bscan.shape[0] and 0 <= zi < bscan.shape[1]:
                    bscan[int(z), int(zi), :] = color

    img = Image.fromarray(bscan)

    # 4. Use Matplotlib to display the image and a legend
    fig, ax = plt.subplots(figsize=(20, 12))
    ax.imshow(img)
    ax.axis("off")  # Hide the plot axes

    # Create legend handles
    legend_patches = [
        mpatches.Patch(color=[c / 255.0 for c in colors[j % len(colors)]], label=name)
        for j, name in enumerate(layer_boundary_names)
    ]

    # Display the legend outside the image
    ax.legend(
        handles=legend_patches,
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        title="Boundaries",
    )

    plt.tight_layout()
    plt.show()


def get_etdrs_region(row, laterality):
    """Assigns a data point to an ETDRS region based on laterality."""
    radius = row["radius_mm"]
    angle = row["angle_degrees"]

    r_central = 0.5
    r_inner = 1.5
    r_outer = 3.0

    if radius <= r_central:
        return "Central_Fovea"

    is_superior = 45 <= angle < 135
    is_inferior = -135 <= angle < -45

    # Dynamic logic based on the eye laterality
    if laterality == "L":
        is_temporal = -45 <= angle < 45
        is_nasal = 135 <= angle or angle < -135
    elif laterality == "R":
        is_nasal = -45 <= angle < 45
        is_temporal = 135 <= angle or angle < -135
    else:
        # Default or error case if laterality is not 'L' or 'R'
        is_nasal = False
        is_temporal = False

    if r_central < radius <= r_inner:
        if is_superior:
            return "Inner_Superior"
        if is_inferior:
            return "Inner_Inferior"
        if is_nasal:
            return "Inner_Nasal"
        if is_temporal:
            return "Inner_Temporal"
    elif r_inner < radius <= r_outer:
        if is_superior:
            return "Outer_Superior"
        if is_inferior:
            return "Outer_Inferior"
        if is_nasal:
            return "Outer_Nasal"
        if is_temporal:
            return "Outer_Temporal"
    else:
        return "Outside_Grid"


import pandas as pd


def iqr_filter(
    df: pd.DataFrame,
    cols: list[str],
    k: float = 1.5,
    inplace: bool = False,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Drop rows whose values fall outside [Q1 − k·IQR,  Q3 + k·IQR] for each
    column in `cols`.

    Parameters
    ----------
    df : pd.DataFrame
        Input data.
    cols : list[str]
        Columns to which the IQR filter is applied.
    k : float, optional
        Scale factor (1.5 ≈ Tukey’s classic rule, 3.0 = more conservative).
    inplace : bool, optional
        If True, rows are removed from `df` in-place; otherwise a filtered
        copy is returned.  Default False.
    verbose : bool, optional
        Print how many rows are removed per column.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame (or the original one, if `inplace=True`).
    """
    target = df if inplace else df.copy()

    for col in cols:
        if col not in target.columns:
            raise KeyError(f"Column '{col}' not found in DataFrame")

        q1 = target[col].quantile(0.25)
        q3 = target[col].quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - k * iqr, q3 + k * iqr

        before = len(target)
        target = target[(target[col] >= lo) & (target[col] <= hi)]
        after = len(target)

        if verbose:
            print(
                f"{col}: kept {after:,}/{before:,} rows "
                f"(removed {before - after:,})"
            )

    return target


import os
import sys

import numpy as np
import pandas as pd
import pydicom


def layer_thickness_etdrs_total_avg(seg_file, oct_file):
    """
    Main function to run the complete OCT thickness analysis pipeline.
    """

    try:
        oct_dcm = pydicom.dcmread(oct_file)
        eye_laterality = oct_dcm.ImageLaterality
        seg_dcm = pydicom.dcmread(seg_file)
        segmentation_filename = os.path.splitext(os.path.basename(seg_file))[0]

        seg_pixel_data = seg_dcm.pixel_array
    except FileNotFoundError as e:
        print(
            f"FATAL ERROR: File not found. Please check your file paths. Details: {e}"
        )
        sys.exit()
    except Exception as e:
        print(f"FATAL ERROR: Could not read DICOM files. Details: {e}")
        sys.exit()

    segnum_to_label = {
        int(s.SegmentNumber): s.SegmentLabel for s in seg_dcm.SegmentSequence
    }

    pairs = []

    for i in range(len(seg_dcm.PerFrameFunctionalGroupsSequence)):
        fg = seg_dcm.PerFrameFunctionalGroupsSequence[i]

        instack_number = int(fg.FrameContentSequence[0].InStackPositionNumber)

        segment_number = int(
            fg.SegmentIdentificationSequence[0].ReferencedSegmentNumber
        )

        segment_label = segnum_to_label.get(segment_number, "UNKNOWN")

        pairs.append((instack_number, segment_label))

    # Sort by InStackPositionNumber
    pairs_sorted = sorted(pairs, key=lambda x: x[0])

    # Extract just the labels in stack order
    layer_boundary_names = [label for _, label in pairs_sorted]

    all_thickness_data = []
    num_boundaries, num_slices, num_a_scans = seg_pixel_data.shape

    for i in range(num_slices):
        for zi in range(num_a_scans):
            thickness_at_this_point = {"Slice_Index": i, "A_Scan_Index": zi}
            for j in range(num_boundaries - 1):
                boundary_top_z = seg_pixel_data[j, i, zi]
                boundary_bottom_z = seg_pixel_data[j + 1, i, zi]
                thickness_col_name = f"Thickness_{layer_boundary_names[j]}_to_{layer_boundary_names[j+1]}"
                if boundary_top_z < 0 or boundary_bottom_z < 0:
                    thickness = np.nan
                else:
                    thickness = abs(boundary_bottom_z - boundary_top_z)
                thickness_at_this_point[thickness_col_name] = thickness
            all_thickness_data.append(thickness_at_this_point)

    thickness_df = pd.DataFrame(all_thickness_data)

    try:
        pixel_measures = oct_dcm.SharedFunctionalGroupsSequence[
            0
        ].PixelMeasuresSequence[0]
        z_spacing_mm = pixel_measures.PixelSpacing[0]
        x_spacing_mm = pixel_measures.PixelSpacing[1]
        y_spacing_mm = float(pixel_measures.SliceThickness)

    except (AttributeError, IndexError):
        print("FATAL ERROR: Could not automatically find metadata in the DICOM file.")
        sys.exit()

    # 1. Calculate the physical position (in mm) of each A-scan from the center
    total_width_mm = num_a_scans * x_spacing_mm
    total_height_mm = num_slices * y_spacing_mm
    thickness_df["x_centered_mm"] = (thickness_df["A_Scan_Index"] * x_spacing_mm) - (
        total_width_mm / 2
    )
    thickness_df["y_centered_mm"] = (thickness_df["Slice_Index"] * y_spacing_mm) - (
        total_height_mm / 2
    )
    thickness_df["radius_mm"] = np.sqrt(
        thickness_df["x_centered_mm"] ** 2 + thickness_df["y_centered_mm"] ** 2
    )

    # 2. Filter the DataFrame to keep only points within the 6mm diameter (3mm radius) circle
    etdrs_area_df = thickness_df[thickness_df["radius_mm"] <= 3.0].copy()

    thickness_columns = [col for col in etdrs_area_df.columns if "Thickness_" in col]

    # 3. Calculate the overall average using ONLY the data from the circular area
    overall_avg_pixels = etdrs_area_df[thickness_columns].mean(axis=0)
    overall_avg_mm = overall_avg_pixels * z_spacing_mm
    wide_row_df = overall_avg_mm.to_frame().T

    # --- MODIFICATION END ---

    wide_row_df.insert(0, "File_Name", segmentation_filename)
    wide_row_df.insert(0, "Laterality", eye_laterality)
    wide_row_df.insert(0, "Patient_ID", seg_dcm.PatientID)

    return wide_row_df


def layer_thickness_etdrs(seg_file, oct_file):
    """
    Main function to run the complete OCT thickness analysis pipeline.
    """

    try:
        oct_dcm = pydicom.dcmread(oct_file)
        eye_laterality = oct_dcm.ImageLaterality
        seg_dcm = pydicom.dcmread(seg_file)
        segmentation_filename = os.path.splitext(os.path.basename(seg_file))[0]

        seg_pixel_data = seg_dcm.pixel_array
    except FileNotFoundError as e:
        print(
            f"FATAL ERROR: File not found. Please check your file paths. Details: {e}"
        )
        sys.exit()
    except Exception as e:
        print(f"FATAL ERROR: Could not read DICOM files. Details: {e}")
        sys.exit()

    layer_boundary_names = []
    if "SegmentSequence" in seg_dcm:
        for segment in seg_dcm.SegmentSequence:
            layer_boundary_names.append(segment.SegmentLabel)
    if not layer_boundary_names or len(layer_boundary_names) != seg_pixel_data.shape[0]:
        layer_boundary_names = [f"Boundary_{j}" for j in range(seg_pixel_data.shape[0])]

    all_thickness_data = []
    num_boundaries, num_slices, num_a_scans = seg_pixel_data.shape

    for i in range(num_slices):
        for zi in range(num_a_scans):
            thickness_at_this_point = {"Slice_Index": i, "A_Scan_Index": zi}
            for j in range(num_boundaries - 1):
                boundary_top_z = seg_pixel_data[j, i, zi]
                boundary_bottom_z = seg_pixel_data[j + 1, i, zi]
                thickness_col_name = f"Thickness_{layer_boundary_names[j]}_to_{layer_boundary_names[j+1]}"
                if boundary_top_z < 0 or boundary_bottom_z < 0:
                    thickness = np.nan
                else:
                    thickness = abs(boundary_bottom_z - boundary_top_z)
                thickness_at_this_point[thickness_col_name] = thickness
            all_thickness_data.append(thickness_at_this_point)

    thickness_df = pd.DataFrame(all_thickness_data)

    try:
        pixel_measures = oct_dcm.SharedFunctionalGroupsSequence[
            0
        ].PixelMeasuresSequence[0]
        z_spacing_mm = pixel_measures.PixelSpacing[0]
        x_spacing_mm = pixel_measures.PixelSpacing[1]
        y_spacing_mm = float(pixel_measures.SliceThickness)

    except (AttributeError, IndexError):
        print("FATAL ERROR: Could not automatically find metadata in the DICOM file.")
        sys.exit()

    total_width_mm = num_a_scans * x_spacing_mm
    total_height_mm = num_slices * y_spacing_mm
    thickness_df["x_centered_mm"] = (thickness_df["A_Scan_Index"] * x_spacing_mm) - (
        total_width_mm / 2
    )
    thickness_df["y_centered_mm"] = (thickness_df["Slice_Index"] * y_spacing_mm) - (
        total_height_mm / 2
    )

    thickness_df["radius_mm"] = np.sqrt(
        thickness_df["x_centered_mm"] ** 2 + thickness_df["y_centered_mm"] ** 2
    )
    thickness_df["angle_degrees"] = np.degrees(
        np.arctan2(thickness_df["y_centered_mm"], thickness_df["x_centered_mm"])
    )

    thickness_df["ETDRS_Region"] = thickness_df.apply(
        lambda row: get_etdrs_region(row, eye_laterality), axis=1
    )

    thickness_columns = [col for col in thickness_df.columns if "Thickness_" in col]
    etdrs_results_pixels = (
        thickness_df.groupby("ETDRS_Region")[thickness_columns].mean().sort_index()
    )
    etdrs_results_mm = etdrs_results_pixels * z_spacing_mm

    final_combined_df = etdrs_results_mm
    flattened = final_combined_df.copy()
    flattened.index.name = "Region"
    flattened.columns.name = "Layer"
    flattened = flattened.stack().rename("Thickness_mm").reset_index()

    flattened["Combined_Col"] = flattened["Region"] + "_" + flattened["Layer"]
    wide_row_df = flattened.pivot_table(
        index=None, columns="Combined_Col", values="Thickness_mm"
    )

    wide_row_df.insert(0, "File_Name", segmentation_filename)
    wide_row_df.insert(0, "Laterality", eye_laterality)
    wide_row_df.insert(0, "Patient_ID", seg_dcm.PatientID)

    return wide_row_df


import matplotlib.pyplot as plt
import pandas as pd


def describe_and_hist(df, bins=30):
    """
    Prints key summary stats and plots a histogram for each numeric
    column in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data you want to explore.
    bins : int, default 30
        Number of histogram bins.
    """

    # 1. Select only the columns that are numeric
    numeric_cols = df.select_dtypes(include="number").columns

    # 2. Exclude any column named 'patient_id'
    cols_to_analyze = [col for col in numeric_cols if col != "person_id"]

    # 3. Loop through each of the selected column names
    for col_name in cols_to_analyze:
        print(f"--- Analysis for column: {col_name} ---")

        # Get the specific column (Series) and remove any missing values
        series = df[col_name].dropna()

        # If the column is empty after removing NaNs, skip it
        if series.empty:
            print("Column contains no data. Skipping.\n")
            continue

        # 4. Compute and print the summary statistics
        stats = pd.Series(
            {
                "count": series.count(),
                "mean": series.mean(),
                "min": series.min(),
                "25%": series.quantile(0.25),
                "median": series.median(),
                "75%": series.quantile(0.75),
                "max": series.max(),
            }
        )
        print(stats)

        # 5. Plot the histogram for the current column
        plt.figure(figsize=(8, 5))
        series.hist(bins=bins)
        plt.title(f"Histogram of {col_name}")
        plt.xlabel(col_name)
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.show()
        print("-" * 40 + "\n")  # Add a separator for clarity
