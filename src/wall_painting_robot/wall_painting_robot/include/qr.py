import cv2
import zxingcpp
import numpy as np

def quick_detect_qr(frame: np.ndarray) -> np.ndarray:
    """Detects QR codes on a live feed in realtime and draws polygons around them."""

    # Detect QR codes in the frame
    decoded_objects = zxingcpp.read_barcodes(frame)

    for obj in decoded_objects:
        # Default color is red for detected QR codes
        color = (0, 0, 255)            

        # If data can be read, set the color to green
        if obj.text and obj.format == zxingcpp.BarcodeFormat.QRCode:
            color = (0, 255, 0)
            
        # Draw polygon around the QR code
        pts = np.intp([(obj.position.top_left.x, obj.position.top_left.y), (obj.position.top_right.x, obj.position.top_right.y), (obj.position.bottom_right.x, obj.position.bottom_right.y), (obj.position.bottom_left.x, obj.position.bottom_left.y)])
        cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)

    return frame
