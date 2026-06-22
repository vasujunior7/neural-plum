from PIL import Image, ImageDraw, ImageFont
import os

output_dir = os.path.join(os.path.dirname(__file__), "test_docs")
os.makedirs(output_dir, exist_ok=True)

def draw_text(draw, x, y, text, size=16, bold=False):
    """Draw text at position - uses default font"""
    try:
        font = ImageFont.truetype("arial.ttf", size)
    except:
        font = ImageFont.load_default()
    draw.text((x, y), text, fill="black", font=font)

# ── Doc 1: Prescription ──
img = Image.new("RGB", (800, 600), "white")
d = ImageDraw.Draw(img)

draw_text(d, 50, 30, "Dr. Arun Sharma, MBBS, MD (Internal Medicine)", 18, True)
draw_text(d, 50, 55, "Reg. No: KA/45678/2015")
draw_text(d, 50, 75, "City Medical Centre, 12 MG Road, Bengaluru")
draw_text(d, 50, 95, "Ph: +91-80-12345678")

d.line([(40, 120), (760, 120)], fill="gray", width=1)

draw_text(d, 50, 135, "Patient: Rajesh Kumar          Date: 01-Nov-2024")
draw_text(d, 50, 160, "Age: 39 years   Gender: Male")
draw_text(d, 50, 185, "Chief Complaint: Fever since 3 days, body ache")

d.line([(40, 210), (760, 210)], fill="gray", width=1)

draw_text(d, 50, 225, "Diagnosis: Viral Fever", 17)

draw_text(d, 50, 260, "Rx:")
draw_text(d, 50, 285, "1. Tab Paracetamol 650mg  -  1-1-1 x 5 days")
draw_text(d, 50, 310, "2. Tab Vitamin C 500mg  -  0-0-1 x 7 days")

draw_text(d, 50, 350, "Investigations: CBC, Dengue NS1")
draw_text(d, 50, 380, "Follow-up: After 5 days if no improvement")

draw_text(d, 500, 450, "[Doctor's Signature]")
draw_text(d, 500, 475, "[Registration Stamp]")

d.rectangle([(30, 20), (770, 520)], outline="black", width=2)

img.save(os.path.join(output_dir, "prescription_rajesh.jpg"), quality=95)
print("Created: prescription_rajesh.jpg")


# ── Doc 2: Hospital Bill ──
img2 = Image.new("RGB", (800, 650), "white")
d2 = ImageDraw.Draw(img2)

draw_text(d2, 250, 30, "CITY MEDICAL CENTRE", 20, True)
draw_text(d2, 220, 55, "12 MG Road, Bengaluru - 560001")
draw_text(d2, 250, 80, "GSTIN: 29ABCDE1234F1Z5")

d2.line([(40, 110), (760, 110)], fill="gray", width=1)

draw_text(d2, 300, 120, "BILL / RECEIPT", 18, True)
draw_text(d2, 50, 150, "Bill No: CMC/2024/08321       Date: 01-Nov-2024")

d2.line([(40, 175), (760, 175)], fill="gray", width=1)

draw_text(d2, 50, 185, "Patient Name: Rajesh Kumar")
draw_text(d2, 50, 210, "Age/Gender: 39 / Male")
draw_text(d2, 50, 235, "Referring Doctor: Dr. Arun Sharma")

d2.line([(40, 260), (760, 260)], fill="gray", width=1)

# Table header
draw_text(d2, 50, 270, "DESCRIPTION", 14)
draw_text(d2, 450, 270, "QTY", 14)
draw_text(d2, 550, 270, "RATE", 14)
draw_text(d2, 650, 270, "AMOUNT", 14)
d2.line([(40, 290), (760, 290)], fill="gray", width=1)

# Line items
draw_text(d2, 50, 300, "Consultation Fee (OPD)")
draw_text(d2, 460, 300, "1")
draw_text(d2, 540, 300, "1000.00")
draw_text(d2, 645, 300, "1000.00")

draw_text(d2, 50, 330, "CBC (Complete Blood Count)")
draw_text(d2, 460, 330, "1")
draw_text(d2, 545, 330, "300.00")
draw_text(d2, 650, 330, "300.00")

draw_text(d2, 50, 360, "Dengue NS1 Antigen Test")
draw_text(d2, 460, 360, "1")
draw_text(d2, 545, 360, "200.00")
draw_text(d2, 650, 360, "200.00")

d2.line([(40, 395), (760, 395)], fill="gray", width=1)

draw_text(d2, 450, 405, "Subtotal:")
draw_text(d2, 645, 405, "1500.00")
draw_text(d2, 450, 430, "GST (0%):")
draw_text(d2, 660, 430, "0.00")
draw_text(d2, 450, 460, "TOTAL:", 16, True)
draw_text(d2, 640, 460, "1500.00", 16, True)

d2.line([(40, 495), (760, 495)], fill="gray", width=1)

draw_text(d2, 50, 510, "Payment Mode: Cash")
draw_text(d2, 500, 510, "[Cashier Stamp]")

d2.rectangle([(30, 20), (770, 560)], outline="black", width=2)

img2.save(os.path.join(output_dir, "hospital_bill_rajesh.jpg"), quality=95)
print("Created: hospital_bill_rajesh.jpg")

# --- Function to quickly generate standard dummy docs ---
def create_dummy_doc(filename, title, patient, content_lines, doc_type="PRESCRIPTION"):
    img = Image.new("RGB", (800, 600), "white")
    d = ImageDraw.Draw(img)
    draw_text(d, 50, 30, title, 18, True)
    d.line([(40, 80), (760, 80)], fill="gray", width=1)
    draw_text(d, 50, 100, f"Patient: {patient}")
    draw_text(d, 50, 125, f"Document Type: {doc_type}")
    d.line([(40, 160), (760, 160)], fill="gray", width=1)
    
    y = 180
    for line in content_lines:
        draw_text(d, 50, y, line)
        y += 25
        
    d.rectangle([(30, 20), (770, 580)], outline="black", width=2)
    img.save(os.path.join(output_dir, filename), quality=95)
    print(f"Created: {filename}")

# TC013: Dependent Claim (Sunita Kumar)
create_dummy_doc("tc013_prescription.jpg", "Dr. Anjali Desai, General Physician", "Sunita Kumar", 
                 ["Diagnosis: Seasonal Flu", "Rx: Paracetamol 500mg"])
create_dummy_doc("tc013_bill.jpg", "City Medical Centre", "Sunita Kumar", 
                 ["Line Items:", "1. Consultation - 1000.00", "TOTAL: 1000.00"], "HOSPITAL BILL")

# TC014: Pharmacy Branded
create_dummy_doc("tc014_prescription.jpg", "Dr. Ravi, Pulmonologist", "Amit Verma", 
                 ["Diagnosis: Asthma", "Rx: Seretide Evohaler (Branded)"])
create_dummy_doc("tc014_bill.jpg", "Apollo Pharmacy", "Amit Verma", 
                 ["Line Items:", "1. Seretide Evohaler - 2000.00", "TOTAL: 2000.00"], "PHARMACY BILL")

# TC015: Vision LASIK
create_dummy_doc("tc015_prescription.jpg", "Vision Eye Care", "Sneha Reddy", 
                 ["Diagnosis: Myopia", "Recommended: Eye Exam and LASIK Surgery"])
create_dummy_doc("tc015_bill.jpg", "Vision Eye Care", "Sneha Reddy", 
                 ["Line Items:", "1. Eye Examination - 2000.00", "2. LASIK Surgery - 40000.00", "TOTAL: 42000.00"], "HOSPITAL BILL")

# TC016: Maternity Waiting Period
create_dummy_doc("tc016_prescription.jpg", "Motherhood Hospital", "Kavita Nair", 
                 ["Diagnosis: Pregnancy (Routine Checkup)"])
create_dummy_doc("tc016_bill.jpg", "Motherhood Hospital", "Kavita Nair", 
                 ["Line Items:", "1. Consultation - 2000.00", "TOTAL: 2000.00"], "HOSPITAL BILL")

# TC017: Alternative Medicine
create_dummy_doc("tc017_prescription.jpg", "Vaidya Sharma (AYUR/123)", "Suresh Patil", 
                 ["Treatment: Ayurvedic Massage Therapy"])
create_dummy_doc("tc017_bill.jpg", "Ayurvedic Healing Center", "Suresh Patil", 
                 ["Line Items:", "1. Massage Therapy - 1500.00", "TOTAL: 1500.00"], "HOSPITAL BILL")

print(f"\nAll test docs saved to: {output_dir}")
