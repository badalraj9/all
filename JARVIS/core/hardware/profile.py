from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import platform
import psutil

@dataclass
class ComputeUnit:
    type: str  # cpu, gpu_cuda, gpu_rocm, gpu_metal, gpu_intel, npu
    vendor: str
    model: str
    cores: Any  # Dict for CPU {physical, logical}, Int for GPU
    clock_mhz: float
    memory_gb: float # VRAM or Cache
    capabilities: List[str] # AVX512, CUDA 8.9, etc.
    score: int
    available: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MemoryInfo:
    total_gb: float
    available_gb: float
    used_gb: float
    type: str # DDR4, DDR5, Unknown
    speed_mhz: float
    swap_total_gb: float
    swap_used_gb: float
    score: int

@dataclass
class StorageInfo:
    type: str # nvme, ssd, hdd
    total_gb: float
    free_gb: float
    read_speed_mbps: float
    write_speed_mbps: float
    score: int
    path: str

@dataclass
class HardwareProfile:
    system_id: str
    timestamp: str
    compute_units: List[ComputeUnit]
    memory: MemoryInfo
    storage: StorageInfo
    overall_score: int

    def to_dict(self):
        import dataclasses
        return dataclasses.asdict(self)

def detect_hardware() -> HardwareProfile:
    """
    Simplified assimilation of MAREY's detector.
    """
    # CPU
    cpu_freq = psutil.cpu_freq()
    cpu_clock = cpu_freq.current if cpu_freq else 0.0
    cpu_cores = {
        "physical": psutil.cpu_count(logical=False),
        "logical": psutil.cpu_count(logical=True)
    }

    cpu_unit = ComputeUnit(
        type="cpu",
        vendor=platform.processor(),
        model=platform.machine(),
        cores=cpu_cores,
        clock_mhz=cpu_clock,
        memory_gb=0, # CPU cache hard to get via psutil
        capabilities=[],
        score=100 # Placeholder scoring
    )

    # Memory
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    memory = MemoryInfo(
        total_gb=vm.total / (1024**3),
        available_gb=vm.available / (1024**3),
        used_gb=vm.used / (1024**3),
        type="Unknown",
        speed_mhz=0.0,
        swap_total_gb=swap.total / (1024**3),
        swap_used_gb=swap.used / (1024**3),
        score=int(vm.total / (1024**3) * 10) # Simple scoring
    )

    # Storage
    disk = psutil.disk_usage('/')
    storage = StorageInfo(
        type="Unknown",
        total_gb=disk.total / (1024**3),
        free_gb=disk.free / (1024**3),
        read_speed_mbps=0.0,
        write_speed_mbps=0.0,
        score=50,
        path="/"
    )

    return HardwareProfile(
        system_id=platform.node(),
        timestamp=str(time.time()),
        compute_units=[cpu_unit],
        memory=memory,
        storage=storage,
        overall_score=cpu_unit.score + memory.score
    )

import time
