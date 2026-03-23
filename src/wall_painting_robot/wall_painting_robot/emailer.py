from email.message import EmailMessage
import os
import smtplib
import mimetypes
import shutil

print("Beginning email script")

sender_email = "emilyrose5567@gmail.com"
receiver_email = "jacobrejin@gmail.com" #CHANGE TO LUCAS, REJIN, OR TEJAS
password = "udrq pprb cabl gtbs" 

msg = EmailMessage()
msg["Subject"] = "QR codes"
msg["From"] = sender_email
msg["To"] = receiver_email
body = []

tmp_dir = "/home/ORT_QR"
email_dir = "/home/ORT_QR/to_email"
textfile = "/home/ORT_QR/rock_detections.txt"
summary_path = "/home/ORT_QR/final_rock_submission.txt"

# Iterate through rock folders
rock_folders = {
    d: os.path.join(tmp_dir, d)
    for d in os.listdir(tmp_dir)
    if os.path.isdir(os.path.join(tmp_dir, d)) and d.startswith("rock")
}

email_folders = [
    
    os.path.join(email_dir, d)
    for d in os.listdir(email_dir)
    if os.path.isdir(os.path.join(email_dir, d)) and d.startswith("rock")
]
for folder_path in email_folders:
    folder_name = os.path.basename(folder_path)

    # Find the matching rock folder
    rock_folder_path = rock_folders.get(folder_name)

    if rock_folder_path:
        # Copy the .txt file(s) into the email folder
        for file in os.listdir(rock_folder_path):
            if file.endswith(".txt"):
                source_path = os.path.join(rock_folder_path, file)
                dest_path = os.path.join(folder_path, file)
                shutil.copy(source_path, dest_path)

    # Attach each file in the email folder
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        with open(file_path, "rb") as f:
            file_data = f.read()
            maintype, subtype = mimetypes.guess_type(file_path)[0].split("/")
            msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file)
        #search for data
        name, _ = os.path.splitext(file)
        name = name[len("rock_image_"):]
        with open(textfile, "r") as log_file:
            for line in log_file:
                if line.startswith(f"Image {name}"):
                    body.append(line)

with open(summary_path, "w") as f:
        f.write("\n".join(body))
with open(summary_path, "rb") as f:
        data = f.read()
msg.add_attachment(data, maintype="text", subtype="plain", filename=os.path.basename(summary_path))

print("ensure only one image and summary file in each email folder")
input("Press Enter to continue...")


try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.send_message(msg)
    print("✅ Email sent successfully.")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
            
