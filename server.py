#!/usr/bin/env python3
import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from datetime import datetime, timedelta

# Global in-memory stores
ORDERS = {}
SHIPMENTS = {}

# Initialize with some sample data
def init_sample_data():
    global ORDERS, SHIPMENTS
    
    # Sample orders
    ORDERS["ORD-1001"] = {
        "id": "ORD-1001",
        "receivedAt": "2025-08-21T10:30:00Z",
        "status": "customerActionRequired",
        "customerId": "CUST-001",
        "total": 156.99,
        "items": [
            {"id": "ITEM-1", "name": "Wireless Headphones", "description": "High-quality headphones", "quantity": 1, "price": 99.99},
            {"id": "ITEM-2", "name": "Phone Case", "description": "Protective case", "quantity": 2, "price": 28.50}
        ]
    }
    
    ORDERS["ORD-1002"] = {
        "id": "ORD-1002",
        "receivedAt": "2025-08-20T14:15:00Z",
        "status": "pending",
        "customerId": "CUST-002",
        "total": 89.99,
        "items": [
            {"id": "ITEM-3", "name": "Bluetooth Speaker", "description": "Portable speaker", "quantity": 1, "price": 89.99}
        ]
    }
    
    # Sample shipments
    SHIPMENTS["SHIP-3001"] = {
        "id": "SHIP-3001",
        "orderId": "ORD-1001",
        "tracking": "TRK123456",
        "status": "booked",
        "estimatedDelivery": "2025-08-24T12:00:00Z",
        "items": [
            {"id": "ITEM-1", "name": "Wireless Mouse", "description": "Ergonomic mouse", "quantity": 1, "price": 29.99},
            {"id": "ITEM-2", "name": "Keyboard", "description": "Mechanical keyboard", "quantity": 1, "price": 79.99}
        ]
    }
    
    SHIPMENTS["SHIP-3002"] = {
        "id": "SHIP-3002",
        "orderId": "ORD-1002",
        "tracking": "TRK789012",
        "status": "booked",
        "estimatedDelivery": "2025-08-25T15:00:00Z",
        "items": [
            {"id": "ITEM-4", "name": "USB Cable", "description": "USB-C cable", "quantity": 1, "price": 15.99}
        ]
    }

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.build_dir = "build"
        super().__init__(*args, directory=self.build_dir, **kwargs)
    
    def do_GET(self):
        self.handle_request("GET")
    
    def do_POST(self):
        self.handle_request("POST")
    
    def do_PUT(self):
        self.handle_request("PUT")
    
    def do_DELETE(self):
        self.handle_request("DELETE")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def handle_request(self, method):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        print(f"\n🌐 {method} {self.path}")
        if parsed_path.query:
            print(f"   Query: {parsed_path.query}")
        
        if path.startswith('/api'):
            self.handle_api_request(method, path, parsed_path.query)
            return
        
        if method == "GET":
            file_path = os.path.join(self.build_dir, path.lstrip('/'))
            
            if path == '/' or path == '':
                file_path = os.path.join(self.build_dir, 'index.html')
            elif os.path.isdir(file_path):
                file_path = os.path.join(file_path, 'index.html')
            elif not os.path.exists(file_path):
                if not any(path.endswith(ext) for ext in ['.js', '.css', '.png', '.jpg', '.ico', '.svg', '.woff', '.woff2']):
                    print(f"   📄 SPA fallback: serving index.html for {path}")
                    file_path = os.path.join(self.build_dir, 'index.html')
                else:
                    print(f"   ❌ Static asset not found: {path}")
            
            if file_path.endswith('index.html'):
                self.path = '/index.html'
            
            super().do_GET()
        else:
            self.send_error(405, f"Method {method} not allowed for static files")
    
    def handle_api_request(self, method, path, query):
        global ORDERS, SHIPMENTS
        
        print(f"   🔌 API Request: {method} {path}")
        
        # Read request body if present
        body_data = None
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            try:
                body_data = json.loads(body.decode('utf-8'))
                print(f"   📦 Body: {json.dumps(body_data, indent=2)}")
            except:
                print(f"   📦 Body: {body.decode('utf-8', errors='ignore')}")
        
        # Route API calls
        if path == "/api/orders" and method == "GET":
            response = {"orders": list(ORDERS.values())}
            
        elif path.startswith("/api/orders/") and method == "GET":
            order_id = path.split("/")[-1]
            if order_id in ORDERS:
                response = {"order": ORDERS[order_id]}
            else:
                response = {"error": "Order not found"}
                
        elif path == "/api/order" and method == "POST":
            # Create new order
            if body_data and "order" in body_data:
                order = body_data["order"]
                order_id = order.get("id", f"ORD-{len(ORDERS) + 1000}")
                order["id"] = order_id
                order["status"] = "pending"
                order["receivedAt"] = datetime.now().isoformat()
                ORDERS[order_id] = order
                print(f"   ✅ Created order: {order_id}")
                response = {"status": "success", "orderId": order_id}
            else:
                response = {"error": "Invalid order data"}
                
        elif path == "/api/order-action" and method == "POST":
            # Update order status
            if body_data:
                order_id = body_data.get("id")
                action = body_data.get("action")
                if order_id in ORDERS:
                    if action == "cancel":
                        ORDERS[order_id]["status"] = "cancelled"
                    elif action == "amend":
                        ORDERS[order_id]["status"] = "processing"
                    print(f"   ✅ Updated order {order_id} status: {ORDERS[order_id]['status']}")
                    response = {"status": "success"}
                else:
                    response = {"error": "Order not found"}
            else:
                response = {"error": "Invalid request"}
                
        elif path == "/api/shipments" and method == "GET":
            response = {"shipments": list(SHIPMENTS.values())}
            
        elif path.startswith("/api/shipments/") and method == "GET":
            shipment_id = path.split("/")[-1]
            if shipment_id in SHIPMENTS:
                response = {"shipment": SHIPMENTS[shipment_id]}
            else:
                response = {"error": "Shipment not found"}
                
        elif path == "/api/shipment" and method == "POST":
            # Update shipment status
            if body_data:
                shipment_data = body_data.get("shipment", {})
                signal = body_data.get("signal", {})
                shipment_id = shipment_data.get("id")
                new_status = signal.get("status")
                
                if shipment_id in SHIPMENTS and new_status:
                    SHIPMENTS[shipment_id]["status"] = new_status
                    print(f"   ✅ Updated shipment {shipment_id} status: {new_status}")
                    response = {"status": "success"}
                else:
                    response = {"error": "Shipment not found or invalid status"}
            else:
                response = {"error": "Invalid request"}
                
        else:
            response = {"error": "Endpoint not found"}
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def log_message(self, format, *args):
        """Override to reduce default logging noise"""
        pass

def main():
    PORT = 5173
    
    # Initialize sample data
    init_sample_data()
    print(f"📦 Initialized {len(ORDERS)} orders and {len(SHIPMENTS)} shipments")
    
    # Check if build directory exists
    build_path = Path("build")
    if not build_path.exists():
        print(f"❌ Build directory not found: {build_path}")
        print("   Run 'npm run build' first")
        return
    
    print(f"🚀 Starting SPA server on http://localhost:{PORT}")
    print(f"📁 Serving files from: {build_path.absolute()}")
    print(f"🔌 API calls will be logged and handled by in-memory store")
    print(f"   Press Ctrl+C to stop\n")
    
    try:
        with socketserver.TCPServer(("", PORT), SPAHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n👋 Server stopped")

if __name__ == "__main__":
    main()