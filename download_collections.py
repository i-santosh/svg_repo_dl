"""
SVG Repo Collection Downloader - Simple & Fast
"""
import json
import os
import subprocess
import concurrent.futures
from tqdm import tqdm

def load_collections(json_path: str):
    """Load collection URLs from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)

def download_collection(url: str, download_dir: str):
    """Download a single collection."""
    collection_name = url.rstrip('/').split('/')[-1]
    
    try:
        # Set environment to handle Unicode properly
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            ["svgrepodl", url], 
            cwd=download_dir,  # Run directly in the main download directory
            capture_output=True, 
            text=True, 
            check=True,
            env=env,
            encoding='utf-8',
            errors='replace'
        )
        return f"✓ {collection_name}"
    except subprocess.CalledProcessError as e:
        return f"✗ {collection_name}: {e.stderr.strip() if e.stderr else 'Failed'}"

def main():
    # Setup
    script_dir = os.path.dirname(os.path.abspath(__file__))
    collections = load_collections(os.path.join(script_dir, "collections.json"))
    download_dir = os.path.join(script_dir, "svg_repo_downloads")
    os.makedirs(download_dir, exist_ok=True)
    
    print(f"Downloading {len(collections)} collections with 12 workers...")
    
    # Download with 12 workers (matching your CPU threads)
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(download_collection, url, download_dir) for url in collections]
        
        results = []
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(collections)):
            result = future.result()
            results.append(result)
            
            # Print failures immediately
            if result.startswith("✗"):
                print(f"\n{result}")
    
    # Final count
    successful = len([r for r in results if r.startswith("✓")])
    failed = len([r for r in results if r.startswith("✗")])
    print(f"\nDone! {successful} successful, {failed} failed")

if __name__ == "__main__":
    main()
