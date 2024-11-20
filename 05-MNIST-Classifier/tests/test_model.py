import torch
import pytest
from src.model import MNISTModel
from src.utils import count_parameters, evaluate_model
from torchvision import datasets, transforms
import random
import matplotlib.pyplot as plt
import os
import torchvision.transforms.functional as TF
import numpy as np
import glob
from torchvision.transforms import GaussianBlur 

def test_model_parameters():
    model = MNISTModel()
    param_count = count_parameters(model)
    print("\nModel Parameters Verification:")
    print("-----------------")
    print(f"Model has {param_count} parameters\n")
    assert param_count < 25000, f"Model has {param_count} parameters, should be less than 25000"

def test_input_output_shape():
    model = MNISTModel()
    test_input = torch.randn(1, 1, 28, 28)
    output = model(test_input)
    print("\nOutput Shape Verification:")
    print("-----------------")
    print(f"Output shape is {output.shape}, should be (1, 10)\n")
    assert output.shape == (1, 10), f"Output shape is {output.shape}, should be (1, 10)"

def test_model_accuracy():
    model = MNISTModel()
    # Train the model first
    from src.train import train
    model_path = train()
    
    # Load the trained model
    model.load_state_dict(torch.load(model_path))
    
    # Evaluate
    accuracy = evaluate_model(model)
    print("\nModel Accuracy Verification:")
    print("-----------------")
    print(f"Accuracy: {accuracy}\n")
    assert accuracy > 0.95, f"Model accuracy is {accuracy}, should be > 0.95"

def test_inference_on_samples():
    # Load model
    model = MNISTModel()
    # Get the latest trained model file (using the timestamp suffix)
    import glob
    model_files = glob.glob('model_*.pth')
    latest_model = max(model_files)  # Gets the most recent model file
    model.load_state_dict(torch.load(latest_model))
    model.eval()

    # Load test dataset
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)
    
    # Select 3 random images
    test_samples = []
    true_labels = []
    random.seed(42)  # for reproducibility
    sample_indices = random.sample(range(len(test_dataset)), 3)
    
    # Create output directory for sample images if it doesn't exist
    os.makedirs('test_samples', exist_ok=True)
    
    # Create a figure with 3 subplots
    plt.figure(figsize=(15, 5))
    
    for idx, sample_idx in enumerate(sample_indices):
        image, label = test_dataset[sample_idx]
        test_samples.append(image)
        true_labels.append(label)
        
        # Display the image
        plt.subplot(1, 3, idx + 1)
        plt.imshow(image.squeeze(), cmap='gray')
        plt.title(f'True Label: {label}')
        plt.axis('off')
    
    # Save the figure
    plt.savefig('test_samples/sample_inputs.png')
    plt.close()
    
    # Stack images into a batch
    batch = torch.stack(test_samples)
    
    # Perform inference
    with torch.no_grad():
        outputs = model(batch)
        _, predicted = torch.max(outputs.data, 1)
    
    # Check and display predictions
    print("\nInference Results:")
    print("-----------------")
    for i in range(3):
        print(f"Sample {i+1}: True label = {true_labels[i]}, Predicted = {predicted[i]}")
        assert predicted[i] in range(10), f"Prediction {predicted[i]} is not in valid range (0-9)"
    
    # At least 2 out of 3 predictions should be correct
    correct_predictions = sum(1 for pred, true in zip(predicted, true_labels) if pred == true)
    assert correct_predictions >= 2, f"Only {correct_predictions} out of 3 predictions were correct"
    
    print(f"\nSample images have been saved to: test_samples/sample_inputs.png") 

def test_rotation_robustness():
    # Load model
    model = MNISTModel()
    model_files = glob.glob('model_*.pth')
    latest_model = max(model_files)
    model.load_state_dict(torch.load(latest_model))
    model.eval()

    # Load test dataset
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)
    
    # Select 3 random images
    random.seed(42)  # for reproducibility
    sample_indices = random.sample(range(len(test_dataset)), 3)
    
    # Create output directory for rotated samples
    os.makedirs('test_samples/rotation_test', exist_ok=True)
    
    # Test rotation angles
    rotation_angles = [-15, 0, 15]  # degrees
    
    # Create a figure for each sample with its rotations
    plt.figure(figsize=(15, 15))
    
    results = []
    
    for sample_idx, idx in enumerate(sample_indices):
        image, true_label = test_dataset[idx]
        
        # Create subplot row for this sample
        for angle_idx, angle in enumerate(rotation_angles):
            plt.subplot(3, 3, sample_idx * 3 + angle_idx + 1)
            
            # Rotate image
            rotated_image = TF.rotate(image, angle)
            
            # Display rotated image
            plt.imshow(rotated_image.squeeze(), cmap='gray')
            
            # Make prediction
            with torch.no_grad():
                output = model(rotated_image.unsqueeze(0))
                _, predicted = torch.max(output.data, 1)
                predicted_label = predicted.item()
            
            results.append({
                'sample': sample_idx + 1,
                'angle': angle,
                'true_label': true_label,
                'predicted_label': predicted_label,
                'correct': true_label == predicted_label
            })
            
            plt.title(f'Sample {sample_idx + 1}\nRotation: {angle}°\nTrue: {true_label}, Pred: {predicted_label}')
            plt.axis('off')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig('test_samples/rotation_test/rotated_samples.png')
    plt.close()
    
    # Print results
    print("\nRotation Robustness Results:")
    print("-" * 50)
    for result in results:
        print(f"Sample {result['sample']}, "
              f"Rotation {result['angle']:>3}°: "
              f"True={result['true_label']}, "
              f"Predicted={result['predicted_label']} "
              f"({'✓' if result['correct'] else '✗'})")
    
    # Calculate accuracy for each rotation
    for angle in rotation_angles:
        angle_results = [r for r in results if r['angle'] == angle]
        correct = sum(1 for r in angle_results if r['correct'])
        print(f"\nAccuracy at {angle}° rotation: {correct}/{len(angle_results)}")
    
    # Assertions for robustness
    # At least 2 out of 3 predictions should be correct for each rotation angle
    for angle in rotation_angles:
        angle_results = [r for r in results if r['angle'] == angle]
        correct = sum(1 for r in angle_results if r['correct'])
        assert correct >= 2, f"Poor performance at {angle}° rotation: only {correct}/3 correct"
    
    print(f"\nRotated sample images have been saved to: test_samples/rotation_test/rotated_samples.png")

def test_noise_and_blur_robustness():
    # Load model
    model = MNISTModel()
    model_files = glob.glob('model_*.pth')
    latest_model = max(model_files)
    model.load_state_dict(torch.load(latest_model))
    model.eval()

    # Load test dataset
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)
    
    # Select 3 random images
    random.seed(42)  # for reproducibility
    sample_indices = random.sample(range(len(test_dataset)), 3)
    
    # Create output directory
    os.makedirs('test_samples/perturbation_test', exist_ok=True)
    
    # Create a figure
    plt.figure(figsize=(15, 15))
    
    results = []
    
    # Define perturbation types
    perturbations = [
        ('original', lambda x: x),
        ('gaussian_noise', lambda x: x + torch.randn_like(x) * 0.1),
        ('blur', lambda x: GaussianBlur(kernel_size=5, sigma=(2.0, 2.0))(x.unsqueeze(0)).squeeze(0))
    ]
    
    for sample_idx, idx in enumerate(sample_indices):
        image, true_label = test_dataset[idx]
        
        # Apply each perturbation type
        for pert_idx, (pert_name, pert_func) in enumerate(perturbations):
            plt.subplot(3, 3, sample_idx * 3 + pert_idx + 1)
            
            # Apply perturbation
            perturbed_image = pert_func(image)
            
            # Ensure pixel values are in valid range
            if pert_name == 'gaussian_noise':
                perturbed_image = torch.clamp(perturbed_image, -3, 3)  # Reasonable range for normalized data
            
            # Display perturbed image
            plt.imshow(perturbed_image.squeeze(), cmap='gray')
            
            # Make prediction
            with torch.no_grad():
                output = model(perturbed_image.unsqueeze(0))
                _, predicted = torch.max(output.data, 1)
                predicted_label = predicted.item()
            
            results.append({
                'sample': sample_idx + 1,
                'perturbation': pert_name,
                'true_label': true_label,
                'predicted_label': predicted_label,
                'correct': true_label == predicted_label
            })
            
            plt.title(f'Sample {sample_idx + 1}\n{pert_name}\nTrue: {true_label}, Pred: {predicted_label}')
            plt.axis('off')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig('test_samples/perturbation_test/perturbed_samples.png')
    plt.close()
    
    # Print results
    print("\nNoise and Blur Robustness Results:")
    print("-" * 50)
    for result in results:
        print(f"Sample {result['sample']}, "
              f"Perturbation: {result['perturbation']:<15} "
              f"True={result['true_label']}, "
              f"Predicted={result['predicted_label']} "
              f"({'✓' if result['correct'] else '✗'})")
    
    # Calculate accuracy for each perturbation type
    for pert_name, _ in perturbations:
        pert_results = [r for r in results if r['perturbation'] == pert_name]
        correct = sum(1 for r in pert_results if r['correct'])
        print(f"\nAccuracy with {pert_name}: {correct}/{len(pert_results)}")
    
    # Assertions for robustness
    # At least 2 out of 3 predictions should be correct for each perturbation type
    for pert_name, _ in perturbations:
        pert_results = [r for r in results if r['perturbation'] == pert_name]
        correct = sum(1 for r in pert_results if r['correct'])
        assert correct >= 2, f"Poor performance with {pert_name}: only {correct}/3 correct"
    
    print(f"\nPerturbed sample images have been saved to: test_samples/perturbation_test/perturbed_samples.png")