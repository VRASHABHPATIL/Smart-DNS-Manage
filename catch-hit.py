import json

def parse_json_logs(file_path):
  """Parses a JSON file containing DNS logs.

  Args:
      file_path: The path to the JSON file.

  Returns:
      A list of parsed JSON dictionaries, or an empty list if the file is empty or invalid JSON.
  """
  logs = []
  with open(file_path, 'r') as file:
    for line in file:
      try:
        log = json.loads(line)
        logs.append(log)
      except json.JSONDecodeError:
        pass  # Ignore non-JSON lines silently
  return logs

def parse_non_json_logs(file_path):
  """Parses non-JSON output from dnsmonster using jq (if available).

  This function attempts to convert the output to JSON using jq before parsing.
  It assumes jq is installed and the output format is similar to the sample provided.

  Args:
      file_path: The path to the non-JSON output file.

  Returns:
      A list of parsed JSON dictionaries, or an empty list if parsing fails.
  """
  try:
    import subprocess
    process = subprocess.run(["jq", "-r", '.[] | {"Timestamp": .Timestamp, "DNS": .DNS, "IPVersion": .IPVersion, "SrcIP": .SrcIP, "DstIP": .DstIP, "Protocol": .Protocol, "PacketLength": .PacketLength}'],
                              input=open(file_path), capture_output=True, text=True)
    if process.returncode == 0:
      return json.loads(process.stdout)
    else:
      print(f"Error running jq: {process.stderr}")
  except (ModuleNotFoundError, FileNotFoundError):
    print("jq is not installed or not found in PATH. Skipping non-JSON parsing.")
  return []

def calculate_cache_hit_rate(logs):
  """Calculates the cache hit rate from the parsed logs.

  Args:
      logs: A list of parsed JSON dictionaries containing DNS logs.

  Returns:
      The cache hit rate as a float (0.0 to 1.0) or 0.0 if no valid logs are found.
  """
  hits = 0
  total = 0
  for log in logs:
    if 'DNS' in log and 'Response' in log['DNS']:
      if log['DNS']['Response']:
        hits += 1
      total += 1
    else:
      print(f"Missing 'DNS' or 'Response' key in log: {log}")
  return hits / total if total > 0 else 0

def main():
  """Main function to parse logs, calculate cache hit rate, and print results."""
  file_path = "dns.out"  # Replace with your actual file path

  # Try parsing JSON first
  logs = parse_json_logs(file_path)
  if logs:
    print("Successfully parsed JSON logs.")
  else:
    # Fallback to non-JSON parsing if JSON parsing fails
    logs = parse_non_json_logs(file_path)
    if logs:
      print("Successfully parsed non-JSON logs using jq.")

  if logs:
    cache_hit_rate = calculate_cache_hit_rate(logs)
    print(f"Cache Hit Rate: {cache_hit_rate}")
  else:
    print("No valid logs found for processing.")

if __name__ == "__main__":
  main()

