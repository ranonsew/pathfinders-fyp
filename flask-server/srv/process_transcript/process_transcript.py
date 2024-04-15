from flask import jsonify, request, Flask
from flask_cors import CORS, cross_origin
from werkzeug.datastructures import FileStorage
from pypdf import PdfReader
import requests

app = Flask(__name__)
CORS(app)

courses_url = "http://127.0.0.1:5000/get_all_courses"

#---- Flask Endpoints ----
@app.route('/process_transcript', methods=['POST'])
def process_transcript():
    # Take in PDF file itself. The PDF file should be of DataFile type.

    try:
        # Handle request
        uploaded_file = request.files.get('pdfFile')
        print("PDF file received. Processing.")

        #Read pdf file and split into individual line
        reader = PdfReader(uploaded_file)

        page=[]
        #Split line into individual sections (like course title, grade, cu)
        for i in range(len(reader.pages)):
            page.append(reader.pages[i])
            page[i] = page[i].extract_text().split("\n")

            for j in range(len(page[i])):
                page[i][j] = page[i][j].split("   ")

        courses_result = requests.get(courses_url).json()
        print('Course result:', courses_result)
        course_dict = dict((course['name'], course['id']) for course in courses_result['content'])

        final_dict = {}

        for cur_page in page:
            for cur_list in cur_page:
                if len(cur_list)>=2:
                    if cur_list[1] != "1.0 / 0.0 IP":
                        if course_dict.get(cur_list[0]):
                            final_dict[course_dict[cur_list[0]]] = cur_list[0]

        return jsonify({
            "code": 201,
            "message": "Course extracted successfully.",
            "content": final_dict
        }), 201

    except Exception as e:
        print(e)
        return jsonify({
            "code": 500,
            "message": "Error processing PDF file."
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=True)
