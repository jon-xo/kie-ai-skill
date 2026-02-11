#!/bin/bash
# kie.ai API wrapper for OpenClaw
# Unified API access to multiple AI models (Nano Banana, Veo, Flux, Suno, etc.)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"

usage() {
  cat << EOF
kie.ai API Wrapper v1.0.0
Unified access to AI models: image generation, video, music, and more

USAGE:
  kie-ai.sh <command> [options]

COMMANDS:
  generate-image <prompt>        Generate image with Nano Banana Pro
  watch <task-id>                Watch existing task progress (resume)
  status                         Show active tasks
  models                         List available models
  balance                        Check credit balance
  logs [limit]                   Show recent task logs
  config                         Manage configuration (Google Drive, etc.)
  help                           Show this help

IMAGE GENERATION OPTIONS:
  --model <name>                 Model: nano-banana-pro (default), google/nano-banana, etc.
  --resolution <res>             Resolution: 1K (default), 2K, 4K
  --aspect <ratio>               Aspect ratio: 1:1 (default), 16:9, 9:16
  --output <path>                Output file path (default: auto-generated)
  --upload-drive                 Upload to Google Drive (requires config.json setup)

EXAMPLES:
  # Generate image
  kie-ai.sh generate-image "A serene Japanese garden at sunset"
  
  # Custom resolution and aspect ratio
  kie-ai.sh generate-image "Cyberpunk city" --resolution 2K --aspect 16:9
  
  # Generate and upload to Google Drive
  kie-ai.sh generate-image "Space nebula" --upload-drive
  
  # Resume watching an existing task
  kie-ai.sh watch 177738199f9c8d2ddd0d1a39ad60f0a9
  
  # Show active tasks
  kie-ai.sh status
  
  # Configure Google Drive
  kie-ai.sh config

ENVIRONMENT:
  KIE_API_KEY                    API key (required)
                                 Get from: https://kie.ai/api-key

For more details, see SKILL.md
EOF
}

case "${1:-help}" in
  generate-image)
    shift
    exec "$LIB_DIR/generate-image.py" "$@"
    ;;
  
  watch)
    [[ $# -lt 2 ]] && { echo "Error: watch requires a task-id"; exit 1; }
    shift
    exec "$LIB_DIR/watch_task.py" "$@"
    ;;
  
  status)
    exec "$LIB_DIR/state_manager.py" list
    ;;
  
  models)
    echo "Available Models:"
    echo ""
    echo "IMAGE GENERATION:"
    echo "  nano-banana-pro         - Gemini 3 Pro Image (1K/2K/4K, ~24 credits/image)"
    echo "  google/nano-banana      - Gemini 2.5 Flash Image (basic, cheaper)"
    echo "  google/nano-banana-edit - Image editing"
    echo "  flux-kontext            - Black Forest Labs Flux (high quality)"
    echo "  4o-image                - OpenAI GPT-4o Image"
    echo ""
    echo "VIDEO GENERATION:"
    echo "  veo-3.1                 - Google Veo 3.1 (cinematic)"
    echo "  veo-3.1-fast            - Google Veo 3.1 Fast (cheaper)"
    echo "  runway-aleph            - Runway Gen-4 Aleph"
    echo ""
    echo "MUSIC GENERATION:"
    echo "  suno-v4                 - Suno V4 (up to 8min tracks)"
    echo "  suno-v4.5               - Suno V4.5 Plus"
    echo ""
    echo "See https://docs.kie.ai for full list and pricing"
    ;;
  
  balance)
    shift
    exec "$LIB_DIR/balance.py" "$@"
    ;;
  
  logs)
    echo "View logs at: https://kie.ai/logs"
    ;;
  
  config)
    CONFIG_FILE="$SCRIPT_DIR/config.json"
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
      echo "Creating config.json..."
      cat > "$CONFIG_FILE" << 'JSONEOF'
{
  "drive": {
    "enabled": false,
    "folder_id": "",
    "comment": "Set folder_id to upload generated images to Google Drive. Get folder ID from the URL when viewing the folder."
  }
}
JSONEOF
    fi
    
    cat << 'CONFIGHELP'
Google Drive Upload Configuration
==================================

To enable automatic Google Drive uploads:

1. Get your Google Drive folder ID:
   - Open the folder in your browser
   - Copy the ID from the URL: drive.google.com/drive/folders/YOUR_FOLDER_ID

2. Edit config.json:
   {
     "drive": {
       "enabled": true,
       "folder_id": "YOUR_FOLDER_ID"
     }
   }

3. Ensure MATON_API_KEY is set:
   export MATON_API_KEY="your-key"
   (Get from: https://maton.ai/settings)

4. Ensure Google Drive connection is active:
   See: https://ctrl.maton.ai

Then use --upload-drive flag with generate-image command.

CONFIGHELP
    
    echo "Config file: $CONFIG_FILE"
    echo ""
    cat "$CONFIG_FILE"
    ;;
  
  help|--help|-h)
    usage
    ;;
  
  *)
    echo "Error: Unknown command '$1'"
    echo ""
    usage
    exit 1
    ;;
esac
