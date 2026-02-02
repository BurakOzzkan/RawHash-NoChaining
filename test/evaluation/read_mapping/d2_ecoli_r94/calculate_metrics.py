import argparse
import sys
import os

def parse_paf_ground_truth(paf_path):
    """
    Parses a PAF file and returns a dictionary: {read_name: is_on_target (bool)}.
    Reads with '*' in the target sequence name (column 5, 0-indexed) are Off-Target.
    """
    ground_truth = {}
    try:
        with open(paf_path, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 6:
                    read_name = parts[0]
                    target_name = parts[5]
                    # If target name is '*', it's off-target/unmapped
                    is_on_target = (target_name != '*')
                    ground_truth[read_name] = is_on_target
    except Exception as e:
        print(f"Error reading PAF file: {e}")
        sys.exit(1)
    return ground_truth

def parse_prediction_file(pred_path):
    """
    Parses the prediction file.
    Expected format: <read_name> <status>
    Status can be 1/0, True/False, On/Off, etc.
    Returns a list of tuples: (read_name, is_predicted_on_target)
    """
    predictions = []
    try:
        with open(pred_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Split by whitespace
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                read_name = parts[0]
                status_str = parts[1].lower()
                
                # Determine boolean status
                is_on_target = False
                if status_str == "1":
                    is_on_target = True
                
                predictions.append((read_name, is_on_target))
    except Exception as e:
        print(f"Error reading prediction file: {e}")
        sys.exit(1)
    return predictions

def calculate_metrics(ground_truth, predictions):
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    
    missing_in_gt = 0
    
    for read_name, pred_status in predictions:
        if read_name not in ground_truth:
            # Read present in prediction but not in ground truth PAF
            missing_in_gt += 1
            continue
            
        true_status = ground_truth[read_name]
        
        if true_status and pred_status:
            tp += 1
        elif not true_status and pred_status:
            fp += 1
        elif not true_status and not pred_status:
            tn += 1
        elif true_status and not pred_status:
            fn += 1
            
    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    if missing_in_gt > 0:
        print(f"Warning: {missing_in_gt} reads from prediction file were not found in Ground Truth PAF.")
    
    return {
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "Total": total
    }

def main():
    parser = argparse.ArgumentParser(description="Calculate classification metrics (Accuracy, Precision, Recall, F1) given a Ground Truth PAF and a Prediction file.")
    parser.add_argument("paf_file", help="Path to the Ground Truth PAF file.")
    parser.add_argument("prediction_file", help="Path to the Prediction file (Format: <read_name> <1/0>).")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.paf_file):
        print(f"Error: PAF file not found at {args.paf_file}")
        sys.exit(1)
    if not os.path.exists(args.prediction_file):
        print(f"Error: Prediction file not found at {args.prediction_file}")
        sys.exit(1)
        
    print(f"Reading Ground Truth from: {args.paf_file}")
    gt_map = parse_paf_ground_truth(args.paf_file)
    on_target_count = sum(1 for v in gt_map.values() if v)
    off_target_count = len(gt_map) - on_target_count
    print(f"Loaded {len(gt_map)} reads from Ground Truth ({on_target_count} On-Target, {off_target_count} Off-Target).")
    
    print(f"Reading Predictions from: {args.prediction_file}")
    preds = parse_prediction_file(args.prediction_file)
    print(f"Parsed {len(preds)} predictions.")
    
    if len(preds) == 0:
        print("No valid predictions found.")
        sys.exit(0)
        
    metrics = calculate_metrics(gt_map, preds)
    
    print("-" * 30)
    print("Evaluation Results")
    print("-" * 30)
    print(f"Total Samples: {metrics['Total']}")
    print(f"True Positives (TP): {metrics['TP']}")
    print(f"False Positives (FP): {metrics['FP']}")
    print(f"True Negatives (TN): {metrics['TN']}")
    print(f"False Negatives (FN): {metrics['FN']}")
    print("-" * 30)
    print(f"Accuracy : {metrics['Accuracy']:.4f}")
    print(f"Precision: {metrics['Precision']:.4f}")
    print(f"Recall   : {metrics['Recall']:.4f}")
    print(f"F1 Score : {metrics['F1']:.4f}")
    print("-" * 30)

if __name__ == "__main__":
    main()
