import binascii
import json
import re
from datetime import datetime
from google.protobuf.wrappers_pb2 import StringValue

class Util:
    # helper: decode protobuf attribute name 
    @staticmethod      
    def decode_protobuf_attribute_name(name : str) -> str: 
            try:
                data = json.loads(name)
                hex_value = data.get("value")
                if not hex_value:
                    return "Unknown"

                decoded_bytes = binascii.unhexlify(hex_value)
                
                sv = StringValue()
                try:
                    sv.ParseFromString(decoded_bytes)
                    if(sv.value.strip() == ""):
                        return decoded_bytes.decode("utf-8", errors="ignore").strip()
                    return sv.value.strip()
                except Exception:
                    decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
                    cleaned = ''.join(ch for ch in decoded_str if ch.isprintable())
                    return cleaned.strip()
            except Exception as e:
                print(f"[DEBUG decode] outer exception: {e}")
                return "Unknown"

    