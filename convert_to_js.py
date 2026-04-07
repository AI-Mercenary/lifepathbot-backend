"""
Convert knowledge_base.json to JavaScript file
"""
import json
import sys

# Read the JSON file
with open('app/data/knowledge_base.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Write as JavaScript
with open('processed_data.js', 'w', encoding='utf-8') as f:
    f.write('/**\n')
    f.write(' * EXTRACTED DATA FROM PROCESSED PDF\n')
    f.write(' * Auto-generated from knowledge_base.json\n')
    f.write(' * \n')
    f.write(f' * Document: {data["documents"][0]["title"]}\n')
    f.write(f' * Total Pages: {data["documents"][0]["total_pages"]}\n')
    f.write(f' * Total Paragraphs: {data["metadata"]["total_paragraphs"]}\n')
    f.write(f' * Last Updated: {data["metadata"]["last_updated"]}\n')
    f.write(' */\n\n')
    f.write('const extractedData = ')
    f.write(json.dumps(data, indent=2, ensure_ascii=False))
    f.write(';\n\n')
    f.write('module.exports = extractedData;\n')

print("✓ Successfully created processed_data.js")
