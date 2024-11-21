# Machine Learning Pipeline with test cases using Cursor as code assistant

[![ML Pipeline for MNIST](https://github.com/aiplaybookin/chat-n-code/actions/workflows/ml-pipeline.yml/badge.svg)](https://github.com/aiplaybookin/chat-n-code/actions/workflows/ml-pipeline.yml)

[![codecov](https://codecov.io/github/aiplaybookin/chat-n-code/graph/badge.svg?token=07QBEJBV4Y)](https://codecov.io/github/aiplaybookin/chat-n-code)

## Overview

This repository contains a machine learning pipeline for a MNIST classifier. The pipeline includes a training script, a test script, and a test suite. The test suite includes test cases for the training script and the test script.

# Test Cases

## Test 1: Model Accuracy

## Test 2: Model Parameters

## Test 3: Model Robustness - rotation

## Test 4: Model Robustness - perturbation (noise and blur)

## Test 5: Model Output Shape

To test the code, run the following command:

```bash
pytest tests/ -s  --cov=.  --cov-report=xml:./coverage.xml --cov-report=term
```
