#!/usr/bin/env python3
"""Inspect a PyTorch checkpoint's saved routing tables without materializing tensor storage.

Usage:
    python audit_routing_checkpoint.py /path/to/checkpoint.pt

Requires PyTorch with mmap support. The script prints run/config metadata and tests
whether each saved token_to_expert table is exactly a layer-specific permutation
of token_id % num_experts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch


def plain(value):
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__") and not isinstance(value, dict):
        return vars(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    args = parser.parse_args()

    checkpoint = torch.load(
        args.checkpoint,
        map_location="cpu",
        mmap=True,
        weights_only=False,
    )
    config = plain(checkpoint.get("config", {})) or {}
    run_args = plain(checkpoint.get("args", {})) or {}
    model = checkpoint.get("model", checkpoint.get("state_dict", {}))

    print("step:", checkpoint.get("step"))
    print("config:", json.dumps(config, indent=2, default=str))
    print("args:", json.dumps(run_args, indent=2, default=str))

    route_keys = sorted(k for k in model if k.endswith("token_to_expert"))
    if not route_keys:
        print("No persistent token_to_expert tables found.")
        return

    for key in route_keys:
        route = model[key].long().cpu()
        experts = int(route.max().item()) + 1
        permutation = [int(route[i]) for i in range(experts)]
        expected = torch.tensor(permutation, dtype=torch.long)[
            torch.arange(route.numel()) % experts
        ]
        counts = torch.bincount(route, minlength=experts).tolist()
        print(
            f"{key}: size={route.numel()} counts={counts} "
            f"residue_to_expert={permutation} "
            f"exact_permuted_modulo={bool(torch.equal(route, expected))}"
        )


if __name__ == "__main__":
    main()
