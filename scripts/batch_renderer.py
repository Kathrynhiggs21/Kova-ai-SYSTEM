import os
import sys
import argparse
import logging
import requests
import pandas as pd
from io import StringIO
from google import genai
from google.genai import types

# Setup logging & directory anchors
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("V7.1-Renderer")

OUTPUT_DIRS = [
    "output/front_cards",
    "output/category_backs",
    "output/qa_reports",
    "output/print_assets",
    "output/website_assets",
    "logs"
]

def setup_environment():
    """Ensure all canonical production folders exist."""
    for folder in OUTPUT_DIRS:
        os.makedirs(folder, exist_ok=True)

def initialize_gemini_client():
    """Authenticate with Gemini API using the injected GitHub Secret."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("❌ CRITICAL: GEMINI_API_KEY environment variable is missing.")
        sys.exit(1)
    return genai.Client(api_key=api_key)

def load_dataset(url):
    """Fetch the canonical CSV data from the specified repository source."""
    try:
        logger.info(f"Fetching dataset from: {url}")
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except Exception as e:
        logger.error(f"❌ Failed to download dataset CSV: {e}")
        sys.exit(1)

def run_pipeline():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_url", required=True)
    parser.add_argument("--pilot", default="true")
    args = parser.parse_args()

    setup_environment()
    client = initialize_gemini_client()
    df = load_dataset(args.csv_url)

    # 1. Pilot Gate Enforcement
    is_pilot = args.pilot.lower() == "true"
    if is_pilot:
        logger.info("🚧 Pilot run enabled. Limiting production to a 10-card quality gate.")
        df = df.head(10)
    else:
        logger.info(f"🚀 Full production run initiated for {len(df)} items.")

    qa_log_data = []

    # 2. Sequential/Batch Rendering with Retry/Resume Structure
    for index, row in df.iterrows():
        # Adjust these column keys to match your exact CSV headers
        card_id = row.get("card_id", f"card_{index+1}")
        prompt_text = row.get("prompt", "")
        category = row.get("category", "general")
        
        filename = f"output/front_cards/{card_id}_front.jpg"
        
        # Resume logic: Skip if already rendered in a previous workflow crash
        if os.path.exists(filename):
            logger.info(f"⏭️ Skipping {card_id} (Already exists).")
            continue

        logger.info(f"🎨 Rendering [{card_id}] Template... Prompt Length: {len(prompt_text)} chars")
        
        try:
            # Using Imagen 3 via the updated Gemini API architecture
            result = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=prompt_text,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio="3:4" # Golden standard for standard card dimensions
                )
            )

            # 3. Connect Outputs & Save
            for generated_image in result.generated_images:
                with open(filename, "wb") as f:
                    f.write(generated_image.image.image_bytes)
            
            logger.info(f"✅ Successfully saved: {filename}")
            qa_log_data.append({"card_id": card_id, "status": "SUCCESS", "error": ""})

        except Exception as e:
            logger.error(f"❌ Failed to render card {card_id}: {e}")
            qa_log_data.append({"card_id": card_id, "status": "FAILED", "error": str(e)})

    # 4. Generate QA Reports
    qa_df = pd.DataFrame(qa_log_data)
    qa_df.to_csv("output/qa_reports/production_summary.csv", index=False)
    logger.info("📊 QA Report updated inside output/qa_reports/")

if __name__ == "__main__":
    run_pipeline()