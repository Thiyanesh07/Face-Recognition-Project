import yaml
import os
import faiss
import pickle
import torch
import time
from typing import Optional, Dict, Tuple
import csv
from datetime import datetime, timedelta


def load_config(config_path='config.yaml'):
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            return config
    except Exception as e:
        print(f"Error loading config file: {e}")
        return None

def save_faiss_data(faiss_index, labels, config):
    
    try:
        os.makedirs(config['PATHS']['EMBEDDINGS_DIR'], exist_ok=True)
        index_path = os.path.join(config['PATHS']['EMBEDDINGS_DIR'], config['PATHS']['FAISS_INDEX_FILE'])
        labels_path = os.path.join(config['PATHS']['EMBEDDINGS_DIR'], config['PATHS']['LABELS_FILE'])

        # 1. Save FAISS Index
        faiss.write_index(faiss_index, index_path)
        print(f"FAISS index saved to: {index_path}")

        # 2. Save Labels
        with open(labels_path, 'wb') as f:
            pickle.dump(labels, f)
        print(f"Labels saved to: {labels_path}")

    except Exception as e:
        print(f"Error saving FAISS data: {e}")


def load_faiss_data(config):
    
    index_path = os.path.join(config['PATHS']['EMBEDDINGS_DIR'], config['PATHS']['FAISS_INDEX_FILE'])
    labels_path = os.path.join(config['PATHS']['EMBEDDINGS_DIR'], config['PATHS']['LABELS_FILE'])

    if not os.path.exists(index_path) or not os.path.exists(labels_path):
        print("FAISS index or labels file not found. Run precompute_embeddings.py first.")
        return None, None

    try:
        # 1. Load FAISS Index
        index = faiss.read_index(index_path)
        print(f"FAISS index loaded from: {index_path}")

        # 2. Load Labels
        with open(labels_path, 'rb') as f:
            labels = pickle.load(f)
        print(f"Labels loaded from: {labels_path}")

        return index, labels

    except Exception as e:
        print(f"Error loading FAISS data: {e}")
        return None, None

# Device Management
def get_device(config):
    
    requested_device = (
        str(config.get('DEVICE', None) or config.get('HARDWARE_SETTINGS', {}).get('DEVICE', 'cuda'))
        .lower()
    )

    if requested_device == 'cuda' and torch.cuda.is_available():
        device = 'cuda'
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = 'cpu'
        print("CUDA not available or 'cpu' requested. Using CPU.")

    return device



class DedupeManager:
    
    def __init__(self, same_camera_cooldown: int = 15, cross_camera_cooldown: int = 30,
                 max_accepted_distance: Optional[float] = None):
        self.same_camera_cooldown = same_camera_cooldown
        self.cross_camera_cooldown = cross_camera_cooldown
        self.max_accepted_distance = max_accepted_distance

        
        self._seen_per_cam: Dict[Tuple[str, str], float] = {}
        self._seen_global: Dict[str, float] = {}

    def should_count(self, label: str, camera_name: str, distance: Optional[float] = None) -> bool:
        
        now = time.time()
        if not label or label == 'Unknown':
            return False

        if self.max_accepted_distance is not None and distance is not None:
            if distance > self.max_accepted_distance:
                return False

        last_cam_key = (label, camera_name)
        last_cam_seen = self._seen_per_cam.get(last_cam_key, 0.0)
        if now - last_cam_seen < self.same_camera_cooldown:
            return False

        last_global_seen = self._seen_global.get(label, 0.0)
        if now - last_global_seen < self.cross_camera_cooldown:
            return False

        return True

    def update_seen(self, label: str, camera_name: str):
        now = time.time()
        if not label or label == 'Unknown':
            return
        self._seen_per_cam[(label, camera_name)] = now
        self._seen_global[label] = now


class AttendanceManager:
    
    def __init__(self, cooldown_hours: int = 4, log_file: Optional[str] = None):
        self.cooldown = timedelta(hours=cooldown_hours)
        self.log_file = log_file
        self._last_marked: Dict[str, datetime] = {}

        
        if self.log_file:
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            # Create header file
            if not os.path.exists(self.log_file):
                with open(self.log_file, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["timestamp", "name", "camera"])  # header

    def should_mark(self, name: str) -> bool:
        if not name or name == 'Unknown':
            return False
        now = datetime.now()
        last = self._last_marked.get(name)
        if last and (now - last) < self.cooldown:
            return False
        return True

    def mark(self, name: str, camera_name: str):
        if not name or name == 'Unknown':
            return
        now = datetime.now()
        self._last_marked[name] = now
        if self.log_file:
            with open(self.log_file, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([now.isoformat(timespec='seconds'), name, camera_name])