import requests
import lxml.html
import json
import time


def get_captcha(image_path):
    # This is a dummy function that returns the text of captcha based on the input image.
    # You can replace this with your actual implementation.
    captcha_text = input("Enter captcha text: ")
    return captcha_text


def scrape_driving_license(dl_number, dob):
    # Create session and get the initial page to get cookies and captcha image.
    session = requests.Session()
    initial_url = "https://parivahan.gov.in/rcdlstatus/vahan/rcDlHome.xhtml"
    initial_response = session.get(initial_url)
    initial_tree = lxml.html.fromstring(initial_response.content)

    # Extracting captcha image and the source url.
    captcha_image_src = initial_tree.xpath("//img[@id='form_rcdl:j_idt34:j_idt41']//@src")[0]
    captcha_url = "https://parivahan.gov.in/rcdlstatus/" + captcha_image_src
    captcha_image_response = session.get(captcha_url)

    # Call get_captcha() function to get captcha text.
    captcha_text = get_captcha(captcha_image_response.content)

    # Construct form data for POST request.
    form_data = {
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": "form_rcdl:j_idt46",
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": "form_rcdl:pnl_show form_rcdl:pg_show form_rcdl:rcdl_pnl",
        "form_rcdl:j_idt46": "form_rcdl:j_idt46",
        "form_rcdl": "form_rcdl",
        "form_rcdl:tf_dlNO": dl_number,
        "form_rcdl:tf_dob_input": dob,
        "form_rcdl:j_idt34:CaptchaID": captcha_text,
        "javax.faces.ViewState": initial_tree.xpath("//input[@id='javax.faces.ViewState']/@value")[0],
        "javax.faces.source": "form_rcdl:j_idt34:CaptchaID",
        "javax.faces.partial.event": "blur",
        "javax.faces.partial.execute": "form_rcdl:j_idt34:CaptchaID",
        "javax.faces.partial.render": "form_rcdl:j_idt34:CaptchaID",
    }

    # Here we Make a POST request to submit the form data.
    response = session.post(initial_url, data=form_data)

    # Now we will Check if captcha is invalid.
    if "Invalid Captcha" in response.text:
        print("Invalid captcha, please try again.")
        return None

    # Parse the response to extract the required fields.
    tree = lxml.html.fromstring(response.content)
    name = tree.xpath("//span[contains(text(), 'Holder Name')]/following-sibling::span/text()")[0]
    father_name = tree.xpath("//span[contains(text(), 'Father Name')]/following-sibling::span/text()")[0]
    date_of_issue = tree.xpath("//span[contains(text(), 'Date of Issue')]/following-sibling::span/text()")[0]
    date_of_expiry = tree.xpath("//span[contains(text(), 'Date of Expiry')]/following-sibling::span/text()")[0]
    class_of_vehicle = tree.xpath("//span[contains(text(), 'Class of Vehicle')]/following-sibling::span/text()")[0]

    # Construct and return JSON object.
    result = {
        "Name": name,
        "Father Name": father_name,
        "Date of Issue": date_of_issue,
        "Date of Expiry": date_of_expiry
