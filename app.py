"""
Consent Study Backend API
Flask app for collecting, storing, and exporting consent responses
Deploy to: Heroku, Railway, or your own server
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import json
import csv
import os
from io import StringIO, BytesIO
import pandas as pd
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Data storage (can be replaced with database)
RESPONSES_FILE = 'responses.json'

def load_responses():
    """Load all responses from file"""
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_responses(responses):
    """Save responses to file"""
    with open(RESPONSES_FILE, 'w') as f:
        json.dump(responses, f, indent=2)

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'responses_count': len(load_responses())
    })

@app.route('/api/responses', methods=['POST'])
def submit_response():
    """Submit a new consent study response"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        if 'feedback' not in data or 'ratings' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Add server-side timestamp
        data['server_timestamp'] = datetime.now().isoformat()
        
        # Load existing responses
        responses = load_responses()
        responses.append(data)
        
        # Save
        save_responses(responses)
        
        return jsonify({
            'success': True,
            'message': 'Response recorded',
            'response_id': data.get('sessionId'),
            'total_responses': len(responses)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/responses', methods=['GET'])
def get_responses():
    """Get all responses (with optional filtering)"""
    try:
        responses = load_responses()
        
        # Optional: filter by department
        department = request.args.get('department')
        if department:
            responses = [r for r in responses if r.get('feedback', {}).get('department') == department]
        
        return jsonify({
            'total': len(responses),
            'responses': responses
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/responses/export/json', methods=['GET'])
def export_json():
    """Export all responses as JSON"""
    try:
        responses = load_responses()
        
        output = BytesIO()
        output.write(json.dumps(responses, indent=2).encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'consent_responses_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/responses/export/csv', methods=['GET'])
def export_csv():
    """Export responses as CSV"""
    try:
        responses = load_responses()
        
        # Flatten nested data for CSV
        flat_data = []
        for resp in responses:
            flat_row = {
                'timestamp': resp.get('timestamp'),
                'session_id': resp.get('sessionId'),
                'participant_name': resp.get('feedback', {}).get('participantName', ''),
                'participant_email': resp.get('feedback', {}).get('participantEmail', ''),
                'department': resp.get('feedback', {}).get('department', ''),
                'favorite_design': resp.get('feedback', {}).get('favorite', ''),
                'most_trusted_design': resp.get('feedback', {}).get('mostTrusted', ''),
                'favorite_reason': resp.get('feedback', {}).get('favoriteReason', ''),
                'concerns': resp.get('feedback', {}).get('concerns', ''),
                'total_time_seconds': resp.get('timeSpent', {}).get('totalSeconds', 0),
                'interactions_count': len(resp.get('interactions', [])),
            }
            
            # Add individual ratings
            for variant in ['variant-1', 'variant-2', 'variant-3', 'variant-4', 'variant-5', 'variant-6']:
                flat_row[f'rating_{variant}'] = resp.get('ratings', {}).get(variant, 0)
            
            flat_data.append(flat_row)
        
        # Create DataFrame
        df = pd.DataFrame(flat_data)
        
        # Convert to CSV
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'consent_responses_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/responses/export/excel', methods=['GET'])
def export_excel():
    """Export responses as Excel (.xlsx)"""
    try:
        responses = load_responses()
        
        # Flatten data
        flat_data = []
        for resp in responses:
            flat_row = {
                'Timestamp': resp.get('timestamp'),
                'Session ID': resp.get('sessionId'),
                'Name': resp.get('feedback', {}).get('participantName', ''),
                'Email': resp.get('feedback', {}).get('participantEmail', ''),
                'Department': resp.get('feedback', {}).get('department', ''),
                'Favorite Design': resp.get('feedback', {}).get('favorite', ''),
                'Most Trusted Design': resp.get('feedback', {}).get('mostTrusted', ''),
                'Why Favorite': resp.get('feedback', {}).get('favoriteReason', ''),
                'Concerns': resp.get('feedback', {}).get('concerns', ''),
                'Time Spent (seconds)': resp.get('timeSpent', {}).get('totalSeconds', 0),
                'Interactions': len(resp.get('interactions', [])),
            }
            
            # Add ratings
            for variant_num in range(1, 7):
                variant = f'variant-{variant_num}'
                flat_row[f'Rating - Option {variant_num}'] = resp.get('ratings', {}).get(variant, 0)
            
            flat_data.append(flat_row)
        
        # Create DataFrame
        df = pd.DataFrame(flat_data)
        
        # Write to Excel with formatting
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Responses')
            
            # Get worksheet
            ws = writer.sheets['Responses']
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'consent_responses_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get aggregate statistics"""
    try:
        responses = load_responses()
        
        if not responses:
            return jsonify({'message': 'No responses yet'}), 200
        
        # Calculate stats
        ratings_avg = {}
        favorite_counts = {}
        trust_counts = {}
        
        for resp in responses:
            # Average ratings
            ratings = resp.get('ratings', {})
            for variant, rating in ratings.items():
                if variant not in ratings_avg:
                    ratings_avg[variant] = []
                ratings_avg[variant].append(rating)
            
            # Count favorites
            favorite = resp.get('feedback', {}).get('favorite')
            favorite_counts[favorite] = favorite_counts.get(favorite, 0) + 1
            
            # Count most trusted
            trust = resp.get('feedback', {}).get('mostTrusted')
            trust_counts[trust] = trust_counts.get(trust, 0) + 1
        
        # Calculate averages
        for variant in ratings_avg:
            ratings_avg[variant] = round(sum(ratings_avg[variant]) / len(ratings_avg[variant]), 2)
        
        return jsonify({
            'total_responses': len(responses),
            'average_ratings': ratings_avg,
            'favorite_counts': favorite_counts,
            'most_trusted_counts': trust_counts,
            'last_response': responses[-1].get('timestamp') if responses else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/responses/clear', methods=['POST'])
def clear_responses():
    """Clear all responses (for testing only - protect in production)"""
    # Add authentication in production
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv('ADMIN_API_KEY', 'test-key-change-this'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    save_responses([])
    return jsonify({'success': True, 'message': 'All responses cleared'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
