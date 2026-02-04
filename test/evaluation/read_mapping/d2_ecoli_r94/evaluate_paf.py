#!/usr/bin/env python3

import sys
import os

def parse_gt(gt_file):
    """Parses ground truth PAF and returns a set of mapped read names."""
    gt_mapped_reads = set()
    with open(gt_file, 'r') as f:
        for line in f:
            parts = line.split('\t')
            if len(parts) >= 1:
                read_name = parts[0]
                gt_mapped_reads.add(read_name)
    return gt_mapped_reads

def evaluate(gt_file, pred_file):
    gt_mapped_reads = parse_gt(gt_file)
    encountered_reads = set()
    
    tp = 0
    fp = 0
    fn = 0
    tn = 0
    
    with open(pred_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('\t')
            read_name = parts[0]
            encountered_reads.add(read_name)
            
            # Check format
            is_mapped = False
            if len(parts) == 2 and (parts[1] == '0' or parts[1] == '1'):
                # Format 1: read_name \t 0/1
                is_mapped = (parts[1] == '1')
            elif len(parts) >= 12:
                # Format 2: full PAF, '*' in 6th field (target name) if unmapped
                is_mapped = (parts[5] != '*')
            else:
                # Fallback or unknown format
                print(f"Warning: Unknown format for line: {line}", file=sys.stderr)
                continue

            in_gt = (read_name in gt_mapped_reads)
            
            if is_mapped:
                if in_gt:
                    tp += 1
                else:
                    fp += 1
            else:
                if in_gt:
                    fn += 1
                else:
                    tn += 1
    
    # Calculate metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"Evaluation Results for: {pred_file}")
    print(f"{'='*40}")
    print(f"TP: {tp}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print(f"TN: {tn}")
    print(f"{'-'*40}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"{'='*40}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 evaluate_paf.py <true_mappings.paf> <pred.paf>")
        sys.exit(1)
        
    gt_path = sys.argv[1]
    pred_path = sys.argv[2]
    
    if not os.path.exists(gt_path):
        print(f"Error: GT file not found: {gt_path}")
        sys.exit(1)
    if not os.path.exists(pred_path):
        print(f"Error: Pred file not found: {pred_path}")
        sys.exit(1)
        
    evaluate(gt_path, pred_path)
