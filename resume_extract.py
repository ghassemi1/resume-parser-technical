from pdfminer.high_level import extract_text
text = extract_text("Resume_5_1.pdf")
with open("out/resume_raw.txt","w",encoding="utf-8") as f:
    f.write(text)
print("wrote")
