#!/usr/bin/env python3
"""
JSON Cleanup Script
Removes JSON entries from content.json where the corresponding image files are missing.
Also removes unused images from the images folder.
"""

import json
import os
from urllib.parse import urlparse

def load_json_content(file_path):
    """Load and parse the JSON content file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

def save_json_content(file_path, content):
    """Save content to JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False

def get_missing_images(content, images_folder):
    """Get list of missing image filenames."""
    if not content:
        return []
    
    if not os.path.exists(images_folder):
        print(f"Error: Images folder '{images_folder}' does not exist")
        return []
    
    missing_images = []
    
    try:
        # Get all files in the images folder (lowercase for comparison)
        folder_files = os.listdir(images_folder)
        folder_files_lower = [f.lower() for f in folder_files]
        
        for item in content:
            if 'image' in item:
                image_url = item['image']
                # Extract filename from URL
                parsed_url = urlparse(image_url)
                filename = os.path.basename(parsed_url.path)
                
                if filename:
                    # Check if file exists (case-insensitive)
                    if filename.lower() not in folder_files_lower:
                        missing_images.append(filename)
                        
    except OSError as e:
        print(f"Error accessing images folder: {e}")
    
    return missing_images

def keep_top_elements(content, limit=30):
    """Keep only the top N elements from the content list."""
    if not content:
        return [], []
    
    if len(content) <= limit:
        print(f"Content has {len(content)} elements, which is within the limit of {limit}")
        return content, []
    
    kept_content = content[:limit]
    removed_entries = []
    
    # Track removed entries for reporting
    for i, item in enumerate(content[limit:], limit + 1):
        removed_entries.append({
            'position': i,
            'title': item.get('title', 'No title'),
            'image': item.get('image', 'No image')
        })
    
    return kept_content, removed_entries

def filter_content_by_existing_images(content, images_folder):
    """Filter content to keep only entries with existing images."""
    if not content:
        return [], []
    
    if not os.path.exists(images_folder):
        print(f"Error: Images folder '{images_folder}' does not exist")
        return content, []
    
    filtered_content = []
    removed_entries = []
    
    try:
        # Get all files in the images folder (lowercase for comparison)
        folder_files = os.listdir(images_folder)
        folder_files_lower = [f.lower() for f in folder_files]
        
        for item in content:
            if 'image' in item:
                image_url = item['image']
                # Extract filename from URL
                parsed_url = urlparse(image_url)
                filename = os.path.basename(parsed_url.path)
                
                if filename:
                    # Check if file exists (case-insensitive)
                    if filename.lower() in folder_files_lower:
                        filtered_content.append(item)
                    else:
                        removed_entries.append({
                            'title': item.get('title', 'No title'),
                            'image': filename
                        })
                else:
                    # If no filename, keep the entry
                    filtered_content.append(item)
            else:
                # If no image field, keep the entry
                filtered_content.append(item)
                
    except OSError as e:
        print(f"Error accessing images folder: {e}")
        return content, []
    
    return filtered_content, removed_entries

def get_images_used_in_content(content):
    """Get a set of image filenames used in the content."""
    if not content:
        return set()
    
    used_images = set()
    for item in content:
        if 'image' in item:
            image_url = item['image']
            # Extract filename from URL
            parsed_url = urlparse(image_url)
            filename = os.path.basename(parsed_url.path)
            if filename:
                used_images.add(filename.lower())
    
    return used_images

def remove_unused_images(content, images_folder):
    """Remove images that are not used in the content (except fallbackImage.png)."""
    if not content:
        return []
    
    if not os.path.exists(images_folder):
        print(f"Error: Images folder '{images_folder}' does not exist")
        return []
    
    removed_images = []
    
    try:
        # Get all images currently in the folder
        folder_files = os.listdir(images_folder)
        
        # Get images used in the content
        used_images = get_images_used_in_content(content)
        
        # Always keep fallbackImage.png
        used_images.add('fallbackimage.png')
        
        for filename in folder_files:
            # Check if the file is an image (basic check)
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                if filename.lower() not in used_images:
                    image_path = os.path.join(images_folder, filename)
                    try:
                        os.remove(image_path)
                        removed_images.append(filename)
                        print(f"Removed unused image: {filename}")
                    except OSError as e:
                        print(f"Error removing image {filename}: {e}")
                        
    except OSError as e:
        print(f"Error accessing images folder: {e}")
    
    return removed_images

# New pre-load cleanup: remove images with % in name

def remove_percent_images(images_folder):
    """Delete images with '%' in filename from images folder."""
    if not os.path.exists(images_folder):
        print(f"Error: Images folder '{images_folder}' does not exist")
        return []
    removed = []
    try:
        for filename in os.listdir(images_folder):
            if '%' in filename:
                image_path = os.path.join(images_folder, filename)
                try:
                    os.remove(image_path)
                    removed.append(filename)
                    print(f"Removed image with % in name: {filename}")
                except OSError as e:
                    print(f"Error removing image {filename}: {e}")
    except OSError as e:
        print(f"Error accessing images folder: {e}")
    return removed


def sanitize_asterisks(content):
    """Remove '*' characters from 'title' and 'description' fields."""
    if not content:
        return content, 0
    changes = 0
    for item in content:
        for key in ('title', 'description'):
            if key in item and isinstance(item[key], str):
                new_val = item[key].replace('*', '')
                if new_val != item[key]:
                    item[key] = new_val
                    changes += 1
    return content, changes


def main():
    # Configuration
    content_file = 'content.json'
    images_folder = 'images'
    
    print("=== JSON Cleanup Script ===")
    print(f"Pre-step: Remove images with % in filename")
    print(f"Step 1: Remove entries with missing images")
    print(f"Step 2: Keep only top 30 elements from remaining")
    print(f"Step 3: Remove '*' from title/description")
    print(f"Step 4: Remove unused images from images folder")
    print("-" * 50)

    # Pre-step: remove images with % in filename before loading JSON
    removed_percent = remove_percent_images(images_folder)
    if removed_percent:
        print(f"Removed {len(removed_percent)} images containing % in name before processing JSON")
    else:
        print("No images with % in filename found")
    
    # Load content.json
    content = load_json_content(content_file)
    if content is None:
        return 1
    
    original_count = len(content)
    print(f"Original entries: {original_count}")
    
    # STEP 1: Filter content to keep only entries with existing images
    print(f"\n=== STEP 1: Checking for missing images ===")
    filtered_content, removed_entries = filter_content_by_existing_images(content, images_folder)
    
    if removed_entries:
        print(f"Found {len(removed_entries)} entries with missing images")
        print(f"Entries after image filtering: {len(filtered_content)}")
    else:
        print("✅ All images are present!")
        print(f"Entries after image filtering: {len(filtered_content)}")
    
    # STEP 2: Keep only top 30 elements from the filtered content
    print(f"\n=== STEP 2: Limiting to top 30 elements ===")
    final_content, trimmed_entries = keep_top_elements(filtered_content, 30)
    
    # Show what will be removed in each step
    if removed_entries:
        print(f"\n=== ENTRIES REMOVED (missing images) ({len(removed_entries)}) ===")
        for i, entry in enumerate(removed_entries, 1):
            print(f"{i:2d}. {entry['title']}")
            print(f"    Image: {entry['image']}")
    
    if trimmed_entries:
        print(f"\n=== ENTRIES TRIMMED (keeping only top 30) ({len(trimmed_entries)}) ===")
        for i, entry in enumerate(trimmed_entries, 1):
            print(f"{i:2d}. {entry['title']}")
            print(f"    Position: {entry['position']}")
    
    # STEP 3: Sanitize asterisks from title/description
    print(f"\n=== STEP 3: Removing '*' from title/description ===")
    final_content, sanitize_changes = sanitize_asterisks(final_content)
    if sanitize_changes:
        print(f"Sanitized {sanitize_changes} fields by removing '*'")
    else:
        print("No '*' found in title/description fields")
    
    need_save = bool(removed_entries or trimmed_entries or sanitize_changes)
    
    # Save the final content if any changes occurred
    if need_save:
        if save_json_content(content_file, final_content):
            new_count = len(final_content)
            print(f"\n✅ Successfully updated {content_file}")
            print(f"Original entries: {original_count}")
            print(f"After image filtering: {len(filtered_content)}")
            print(f"Final entries: {new_count}")
            print(f"Total removed: {original_count - new_count}")
        else:
            print(f"\n❌ Failed to save {content_file}")
            return 1
    else:
        print(f"\n✅ No JSON structural changes needed and no '*' to sanitize")
        print(f"All {original_count} entries have existing images and count is within limit of 30")
    
    # STEP 4: Remove unused images from images folder
    print(f"\n=== STEP 4: Removing unused images ===")
    removed_images = remove_unused_images(final_content, images_folder)
    
    if removed_images:
        print(f"Removed {len(removed_images)} unused images from images folder")
        for i, image in enumerate(removed_images, 1):
            print(f"{i:2d}. {image}")
    else:
        print("✅ No unused images found in images folder")
    
    return 0

if __name__ == "__main__":
    exit(main())