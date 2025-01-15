def save_screenshot():
  """Take a screenshot and save it to the 'screenshots' folder with the current date and time as the filename"""
  from PIL import ImageGrab
  import os
  from datetime import datetime

  print(f'🤵🏻 Saving a screenshot...\n')

  # Create the screenshots directory if it doesn't exist
  if not os.path.exists('screenshots'):
    os.makedirs('screenshots')

  # Generate filename using current date and time in the desired format
  filename = "Screenshot " + datetime.now().strftime("%Y-%m-%d at %I.%M.%S %p") + ".png"

  # Capture the screenshot
  screenshot = ImageGrab.grab()
  screenshot.save(os.path.join('screenshots', filename))

  return screenshot