from datetime import datetime
import re

def save_task(task: str, result: str):
  """
  Saves a completed task and its result to a text file.

  Args:
      task (str): The completed task.
      result (str): The result for the task.

  Returns:
      str: The content of the specified XML tag, or an empty string if the tag is not found.
  """
  current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  with open(f"past_tasks/{current_time}.txt", "w") as file:
    task_information = f"Task:\n\n{task}\n\nResult:\n\n{result}\n\nThis task was completed at {current_time}. The task and results are saved to past_tasks/{current_time}.txt."
    file.write(task_information)
  return (task_information)

def extract_xml(text: str, tag: str) -> str:
  """
  Extracts the content of the specified XML tag from the given text. Used for parsing structured responses.

  Args:
      text (str): The text containing the XML.
      tag (str): The XML tag to extract content from.

  Returns:
      str: The content of the specified XML tag, or an empty string if the tag is not found.
  """
  match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
  return match.group(1) if match else ""