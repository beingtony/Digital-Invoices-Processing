import os
import json
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import time
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__, static_folder='static')

# Home route
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/total_transactions')
def total_transactions():
    try:
        # Load JSON data
        data = load_json_data()

        # Calculate total transactions (total number of invoices)
        total_transactions = len(data)

        # Return the result
        return jsonify({"total_transactions": total_transactions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def load_json_data():
    try:
        # Open and load the JSON file
        with open(r'C:\Users\rutuj\OneDrive\Desktop\Applications\Deloitte2\Deloitte-20250313T061155Z-001\Deloitte\ocr_output.json', 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        raise FileNotFoundError("JSON file not found")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON file")
    except Exception as e:
        raise Exception(f"Error loading JSON file: {str(e)}")
    
# Endpoint to fetch the current date
@app.route('/current_date')
def current_date():
    return jsonify({'date': datetime.now().strftime('%Y-%m-%d')})

# Endpoint to fetch invoice data
@app.route('/get_invoices')
def get_invoices():
    try:
        # Path to JSON file
        json_path = r'C:\Users\rutuj\OneDrive\Desktop\Applications\Deloitte2\Deloitte-20250313T061155Z-001\Deloitte\ocr_output.json'        
        # Load JSON data
        with open(json_path, 'r') as file:
            data = json.load(file)
        
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/flag_invoice', methods=['POST'])
def flag_invoice():
    try:
        # Ensure the request has JSON data
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 415

        # Get the invoice_id from the request body
        invoice_id = request.json.get('invoice_id')
        if not invoice_id:
            return jsonify({'error': 'Invoice ID is required'}), 400

        # Path to JSON file
        json_path = r'C:\Users\rutuj\OneDrive\Desktop\Applications\Deloitte2\Deloitte-20250313T061155Z-001\Deloitte\ocr_output.json'
        
        # Load JSON data
        try:
            with open(json_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            return jsonify({'error': 'JSON file not found'}), 404
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON file'}), 400

        # Find and update the invoice status
        invoice_found = False
        for invoice in data:
            if invoice.get('invoice_no') == invoice_id:
                invoice['status'] = 'flagged'
                invoice['flag_date'] = datetime.now().strftime('%d %b %Y')  # Add flag date
                invoice_found = True
                break

        if not invoice_found:
            return jsonify({'error': 'Invoice not found'}), 404

        # Save the updated data back to the JSON file
        try:
            with open(json_path, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            return jsonify({'error': f'Failed to save JSON file: {str(e)}'}), 500

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error flagging invoice: {e}")  # Log the error
        return jsonify({'error': str(e)}), 500

@app.route('/approve_invoice', methods=['POST'])
def approve_invoice():
    try:
        # Ensure the request has JSON data
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 415

        # Get the invoice_id from the request body
        invoice_id = request.json.get('invoice_id')
        if not invoice_id:
            return jsonify({'error': 'Invoice ID is required'}), 400

        # Path to JSON file
        json_path = r'C:\Users\rutuj\OneDrive\Desktop\Applications\Deloitte2\Deloitte-20250313T061155Z-001\Deloitte\ocr_output.json'
        
        # Load JSON data
        try:
            with open(json_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            return jsonify({'error': 'JSON file not found'}), 404
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON file'}), 400

        # Find and update the invoice status
        invoice_found = False
        for invoice in data:
            if invoice.get('invoice_no') == invoice_id:
                invoice['status'] = 'approved'
                invoice['approval_date'] = datetime.now().strftime('%d %b %Y')  # Add approval date
                invoice_found = True
                break

        if not invoice_found:
            return jsonify({'error': 'Invoice not found'}), 404

        # Save the updated data back to the JSON file
        try:
            with open(json_path, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            return jsonify({'error': f'Failed to save JSON file: {str(e)}'}), 500

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error approving invoice: {e}")  # Log the error
        return jsonify({'error': str(e)}), 500
    


@app.route('/monthly_invoice_stats')
def monthly_invoice_stats():
    try:
        # Load invoice data
        with open(r'C:\Users\rutuj\OneDrive\Desktop\Applications\Deloitte2\Deloitte-20250313T061155Z-001\Deloitte\ocr_output.json', 'r') as file:
            invoices = json.load(file)
        
        # Load purchase order data
        with open(r'C:\Users\rutuj\OneDrive\Desktop\Applications\Deloitte2\Deloitte-20250313T061155Z-001\Deloitte\po.json', 'r') as file:
            purchase_orders = json.load(file)
        
        # Initialize monthly totals
        months = ['January', 'February', 'March', 'April', 'May']
        invoice_totals = {month: 0 for month in months}
        po_totals = {month: 0 for month in months}
        
        # Calculate invoice totals by month
        for invoice in invoices:
            month = datetime.strptime(invoice['date'], '%Y-%m-%d').strftime('%B')
            if month in invoice_totals:
                invoice_totals[month] += 1
        
        # Calculate purchase order totals by month
        for po in purchase_orders:
            month = datetime.strptime(po['date'], '%Y-%m-%d').strftime('%B')
            if month in po_totals:
                po_totals[month] += 1
        
        # Prepare response
        response = {
            'labels': months,
            'invoice_totals': [invoice_totals[month] for month in months],
            'po_totals': [po_totals[month] for month in months]
        }
        
        return jsonify(response)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    



# Endpoint to fetch chart data
@app.route('/fetchData')
def fetch_data():
    # Replace this with your actual data fetching logic
    return jsonify({
        'labels': ['January', 'February', 'March', 'April', 'May'],
        'values': [200, 150, 210, 250, 300],
        'pos': [203, 150, 215, 250, 301],
    })

# Endpoint to fetch yearly data
@app.route('/fetchYrs')
def fetch_yrs():
    # Replace this with your actual data fetching logic
    return jsonify({
        'labels': ['2019', '2020', '2021', '2022', '2023', '2024'],
        'values': [130, 170, 290, 350, 300, 330],
        'app': [100, 150, 215, 307, 280, 306],
    })

@app.route('/overall_invoices', methods=['GET'])
def overall_invoices():
    try:
        # Load JSON data
        data = load_json_data()

        # Initialize counters
        under_process = 0
        approved = 0
        flagged = 0

        # Calculate counts
        for invoice in data:
            if invoice['status'] == 'under_process':
                under_process += 1
            elif invoice['status'] == 'approved':
                approved += 1
            elif invoice['status'] == 'flagged':
                flagged += 1

        # Total number of invoices
        total_invoices = len(data)

        # Calculate percentages
        under_process_percent = (under_process / total_invoices) * 100 if total_invoices > 0 else 0
        approved_percent = (approved / total_invoices) * 100 if total_invoices > 0 else 0
        flagged_percent = (flagged / total_invoices) * 100 if total_invoices > 0 else 0

        # Return the counts and percentage changes
        return jsonify({
            'under_process': under_process,
            'approved': approved,
            'flagged': flagged,
            'under_process_percent': round(under_process_percent, 2),  # Round to 2 decimal places
            'approved_percent': round(approved_percent, 2),  # Round to 2 decimal places
            'flagged_percent': round(flagged_percent, 2),  # Round to 2 decimal places
            'total_invoices': total_invoices  # Optional: Return total invoices for reference
        })
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/upload_document', methods=['POST'])
def upload_document():
    try:
        # Check if the request contains a file
        if 'document' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['document']
        doc_type = request.form.get('doc_type', '')

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            # Save the file temporarily
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Simulate processing stages (replace with actual logic)
            stages = [
                f"Uploading {doc_type}...",
                f"Extracting data using OCR...",
                f"Validating {doc_type} details...",
                f"Calculating {doc_type}'s neuro-key...",
                "Processing complete!"
            ]

            # Simulate progress (replace with actual processing logic)
            for stage in stages:
                time.sleep(1)  # Simulate delay for each stage

            # Calculate neuro-key (placeholder logic)
            neuro_key = calculate_neuro_key(doc_type, file_path)

            # Clean up the uploaded file
            os.remove(file_path)

            # Return the result
            return jsonify({"score": neuro_key})
        else:
            return jsonify({"error": "File type not allowed"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}

def calculate_neuro_key(doc_type, file_path):
    """
    Placeholder function to calculate the neuro-key.
    Replace this with actual logic to process the document and calculate the neuro-key.
    """
    if doc_type == "invoice":
        return 85  # Example score for invoice
    elif doc_type == "purchase_order":
        return 92  # Example score for purchase order
    else:
        return 0

# Ensure the upload folder exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    

# Run the app
if __name__ == '__main__':
    app.run(debug=True)