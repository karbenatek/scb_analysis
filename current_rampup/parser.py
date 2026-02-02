import pandas as pd
import numpy as np
from parser import get_metadata


import re
from dataclasses import dataclass
from typing import List, Dict, Any
SOMEFIX = True


def get_RIchar(filepath):
    data = pd.read_csv(filepath)
    
    
    I = data['Current [A]'].to_numpy()
    R = data['Resistance [ohm]'].to_numpy()
    
    metadata = get_metadata(data)
        

    print("Metadata:", metadata)
    return I, R, metadata

def _get_metadata(df):
    header = df.columns.tolist()
    # parse metadata
    s_metadata = ",".join(header)
    s_metadata = s_metadata.split("metadata=[")[1]
    s_metadata = s_metadata[:s_metadata.index("]")]
    # s_metadata = s_metadata[s_metadata.index("metadata=[")+1 : s_metadata.index("]")]

    # split into key=value pairs
    s_metadata = s_metadata.split(",")

    # build dictionary
    metadata = {}
    for p in s_metadata:
        key, value = p.split("=")
        metadata[key] = value
        
    return metadata



@dataclass
class RxI_signal_MeasurementBlock:
    current_A: float
    time_s: List[float]
    resistance_ohm: List[float]


@dataclass
class RxI_signal_ParsedData:
    metadata: Dict[str, Any]
    measurements: List[RxI_signal_MeasurementBlock]


def parse_float_list(s: str) -> List[float]:
    """Convert comma-separated string to float list."""
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def get_RI_signal(filepath: str) -> RxI_signal_ParsedData:
    """Reads the file at `filepath` and parses its content."""

    # ---- Read file ----
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # --------- Parse metadata ----------
    meta_match = re.search(r"metadata=\[(.*?)\]", text, re.DOTALL)
    metadata = {}

    if meta_match:
        meta_raw = meta_match.group(1)
        parts = meta_raw.split(",")

        for p in parts:
            if "=" in p:
                key, val = p.split("=", 1)
                key = key.strip()
                val = val.strip()

                # Try to convert to float (remove "K" if present)
                try:
                    metadata[key] = float(val.rstrip("K"))
                except ValueError:
                    metadata[key] = val

    # ---------- Parse measurement blocks -----------
    block_pattern = re.compile(
        r"I\s*=\s*([0-9.]+)A\s*"
        r"t\s*\[s\]\s*:\s*([0-9.,\s]+)\s*"
        r"R\s*\[ohm\]\s*:\s*([0-9.,\s]+)",
        re.MULTILINE
    )

    measurements = []
    current_prev = -1.0
    for m in block_pattern.finditer(text):
        current = float(m.group(1))
        if SOMEFIX:
            if current == current_prev:
                current += 0.05
        current_prev = current
        t_list = parse_float_list(m.group(2))
        r_list = parse_float_list(m.group(3))

        if len(t_list) != len(r_list):
            raise ValueError(
                f"Mismatched lengths for I={current}: "
                f"{len(t_list)} time values, {len(r_list)} resistance values."
            )

        measurements.append(RxI_signal_MeasurementBlock(
            current_A=current,
            time_s=t_list,
            resistance_ohm=r_list,
        ))

    return RxI_signal_ParsedData(metadata=metadata, measurements=measurements)