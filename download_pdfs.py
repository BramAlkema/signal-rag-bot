#!/usr/bin/env python3
"""Download PDFs from Google Drive URLs"""

import requests
import os
from pathlib import Path

PDF_URLS = [
    "https://drive.google.com/uc?export=download&id=1_sSrBiWhJiSwMJHE1HGyue12fk48-FDY",
    "https://drive.google.com/uc?export=download&id=1LmQoShCF0_VlN3lp818z-puWhruAAtT-",
    "https://drive.google.com/uc?export=download&id=1c9YFRJG1-s3QXq_lPV8WYi0y_zpbKtBJ",
    "https://drive.google.com/uc?export=download&id=1C7KWzAsjorcPV_49873ppZDkPzRzLGH9",
    "https://drive.google.com/uc?export=download&id=1Fq6-jEZ90qe0S3Cb17QjfskuBJYymyPT",
    "https://drive.google.com/uc?export=download&id=1sWqHg38pHDlV8EejsF84EnPu9qWhHKAA",
    "https://drive.google.com/uc?export=download&id=1XCV95r_Ime2KZ0PB-KGzVLfl0ZGyAPNH",
    "https://drive.google.com/uc?export=download&id=1UbwUG29zjUca6ppNsiXuXP0aItw7X5wL",
    "https://drive.google.com/uc?export=download&id=1_pDCzyPhRVU5iS4YDKHLZY941vAMEhM_",
    "https://drive.google.com/uc?export=download&id=1oHA5UTnS8jrqlKe1HzDV-QSmfG6JLdx9",
    "https://drive.google.com/uc?export=download&id=1pzPVwZoKBT3GNiJHdNnjNlSG29wu7S1a",
    "https://drive.google.com/uc?export=download&id=1AgrtfFY_JenMizoSEo9zhldQ-0twZkuG",
    "https://drive.google.com/uc?export=download&id=1b1ma-5vsNOk2SNsATKP1XrE4aRq5_lFY",
    "https://drive.google.com/uc?export=download&id=1Z3f-G8lp61LFyEzt6w7DKnAuU_58BnMr",
    "https://drive.google.com/uc?export=download&id=1g5eS87y3nQmktsKx0uZl6pfLFbIDYvWM",
    "https://drive.google.com/uc?export=download&id=1j9o3uFezRLXgZerggOyfMtHpiukKsM9G",
    "https://drive.google.com/uc?export=download&id=1Llek9uW1b1l-yXV1JnK_E9BE-UbnvhK4",
    "https://drive.google.com/uc?export=download&id=1B3S0LpmO1C0bnz9it-J_obtTqRXk-l99",
    "https://drive.google.com/uc?export=download&id=1O7bnGFHIjWZcu-Z_3Q7UXcHbiSb8pnTF",
]

def download_pdf(url, output_dir="input/pdfs"):
    """Download a PDF from Google Drive"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Extract file ID from URL
    file_id = url.split("id=")[1]

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Save to file
        output_path = os.path.join(output_dir, f"{file_id}.pdf")
        total_size = 0
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                total_size += len(chunk)

        print(f"✓ Downloaded: {file_id}.pdf ({total_size} bytes)")
        return output_path
    except Exception as e:
        print(f"✗ Failed to download {file_id}: {e}")
        return None

if __name__ == "__main__":
    print(f"Downloading {len(PDF_URLS)} PDFs...\n")

    downloaded = 0
    for url in PDF_URLS:
        if download_pdf(url):
            downloaded += 1

    print(f"\n✓ Successfully downloaded {downloaded}/{len(PDF_URLS)} PDFs")
