#!/bin/bash
# Deep Learning Dataset Builder Script
# 
# This script automates the creation of image datasets for deep learning projects
# by downloading images from Google Images for multiple queries.
#
# Usage:
#   ./deeplearning_datasetbuilder.sh <query1> <query2> ... <queryN> <count>
#
# Arguments:
#   query1, query2, ..., queryN: Search queries for images (e.g., "cat" "dog" "bird")
#   count: Number of images to download for each query (last argument)
#
# Examples:
#   ./deeplearning_datasetbuilder.sh "cat" "dog" 50
#   ./deeplearning_datasetbuilder.sh "alien" "robot" "spaceship" 100
#   ./deeplearning_datasetbuilder.sh "Hello World" "Goodbye World" 25
#
# Output:
#   Creates a results/ folder with subfolders for each query
#   Each subfolder has cleaned names (e.g., "Hello World" → "results/hello_world/")
#   Each subfolder contains the downloaded images

set -e  # exit on error

# colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # no color

# function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# function to clean folder names
# converts "Hello World" to "hello_world"
clean_folder_name() {
    local input="$1"
    # convert to lowercase, replace spaces with underscores, remove special chars
    echo "$input" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g' | sed 's/__*/_/g' | sed 's/^_//;s/_$//'
}

# check if enough arguments are provided
if [ $# -lt 2 ]; then
    print_error "Not enough arguments provided"
    echo ""
    echo "Usage: $0 <query1> [query2] ... [queryN] <count>"
    echo ""
    echo "Examples:"
    echo "  $0 \"cat\" \"dog\" 50"
    echo "  $0 \"alien\" \"robot\" \"spaceship\" 100"
    echo ""
    exit 1
fi

# extract the count (last argument)
count="${@: -1}"

# validate that count is a number
if ! [[ "$count" =~ ^[0-9]+$ ]]; then
    print_error "Last argument must be a number (count of images)"
    echo "Got: '$count'"
    exit 1
fi

# validate that count is positive
if [ "$count" -le 0 ]; then
    print_error "Count must be a positive number"
    exit 1
fi

# get all arguments except the last one (these are the queries)
queries=("${@:1:$#-1}")

# validate we have at least one query
if [ ${#queries[@]} -eq 0 ]; then
    print_error "At least one query must be provided"
    exit 1
fi

# print header
echo ""
echo "======================================"
echo "  Deep Learning Dataset Builder"
echo "======================================"
echo ""
print_info "Queries: ${queries[*]}"
print_info "Images per query: $count"
print_info "Total queries: ${#queries[@]}"
print_info "Total images to download: $((${#queries[@]} * count))"
echo ""

# check if dataset_builder.py exists
if [ ! -f "dataset_builder.py" ]; then
    print_error "dataset_builder.py not found in current directory"
    print_info "Please run this script from the alienclassifier directory"
    exit 1
fi

# check if python is available
if ! command -v python3 &> /dev/null; then
    print_error "python3 is not installed or not in PATH"
    exit 1
fi

# track success/failure
total_success=0
total_failed=0
failed_queries=()

# process each query
for query in "${queries[@]}"; do
    # clean the folder name
    folder_name=$(clean_folder_name "$query")
    output_path="results/$folder_name"
    
    print_info "Processing query: '$query'"
    print_info "Output folder: '$output_path/'"
    
    # run the dataset builder
    if python3 dataset_builder.py "$query" --count "$count" --output "$output_path" --headless; then
        print_success "Successfully completed: '$query'"
        ((total_success++))
    else
        print_error "Failed to process: '$query'"
        ((total_failed++))
        failed_queries+=("$query")
    fi
    
    echo ""
done

# print summary
echo "=========" 
echo "  Summary"
echo "========="
print_info "Total queries processed: ${#queries[@]}"
print_success "Successful: $total_success"
if [ $total_failed -gt 0 ]; then
    print_error "Failed: $total_failed"
    if [ ${#failed_queries[@]} -gt 0 ]; then
        echo ""
        print_warning "Failed queries:"
        for failed_query in "${failed_queries[@]}"; do
            echo "  - $failed_query"
        done
    fi
fi
echo ""

# exit with appropriate code
if [ $total_failed -gt 0 ]; then
    exit 1
else
    print_success "All datasets built successfully!"
    exit 0
fi