HydraNexus 💧

Intelligent Water Monitoring

Detect. Analyze. Conserve.

HydraNexus is a Python and Streamlit prototype that demonstrates water-flow monitoring and alerts for sustained high flow.

Features

- Normal usage, possible-leak, and brief-spike scenarios
- Custom water-flow readings
- Adjustable flow threshold
- Configurable consecutive-reading detection
- Water-flow trend chart and monitoring summary
- Reading details and CSV export
- Automated unit tests

Technology Stack

- Python
- Streamlit
- Pandas
- unittest

Requirements

Python 3.10 or newer.

Installation

Create a virtual environment:

python -m venv .venv

Install dependencies:

python -m pip install -r requirements.txt

Run HydraNexus

python -m streamlit run app.py

Run Tests

python -m unittest -v test_detector.py

Current Limitations

HydraNexus currently uses simulated or manually entered readings. It is not connected to physical water-flow sensors and cannot confirm that a real leak exists. Real-world deployment requires sensor integration, appropriate detection rules, and testing.

Project Goal

Demonstrate how software can help monitor water usage, identify sustained high-flow patterns, and support water conservation.