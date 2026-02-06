"""
Test script for collector create wizard

Simulates user input to test the wizard flow
"""

# Test input for psutil/system metrics collector
test_input_cpu = """CPU Usage
1
1
3
cpu.usage
"""

# Test input for shell command collector
test_input_shell = """GPU Temperature
2
nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader
1
2
gpu.temp
"""

# Test input for file parser
test_input_file = """Log Count
3
/var/log/app.log
2
2
log.count
"""

# Test input for API poller
test_input_api = """API Response Time
4
http://localhost:8080/health
2
api.response.time
"""

# Test input for custom plugin
test_input_plugin = """Custom Metric
5
collect_custom
2
custom.metric
"""

if __name__ == '__main__':
    print("Test inputs prepared for collector create wizard")
    print("\nTo test manually:")
    print("  python -m biff_cli collector create -o test_collectors")
    print("\nThen provide input from test_input_cpu, test_input_shell, etc.")
