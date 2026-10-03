"""
Two-route rule: no alert fires on one sensor's word alone.

SNIFF (vapour) and HEAT (swab residue) are independent routes. An "alert" needs both to flag
the item; one route alone only raises "review". Swabbing the same bag twice is NOT two routes.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RouteDecision:
    tier: str            # "clean" | "review" | "alert"
    routes_agreeing: int  # 0, 1 or 2
    reason: str


def fuse_routes(sniff_tier: str, heat_label: str) -> RouteDecision:
    sniff_flag = sniff_tier in ("review", "alert")
    heat_flag = heat_label == "nitro_class"
    heat_unsure = heat_label == "unknown"
    if sniff_flag and heat_flag:
        return RouteDecision("alert", 2, "SNIFF and HEAT agree")
    if heat_flag:
        return RouteDecision("review", 1, "HEAT only, needs a second route")
    if sniff_tier == "alert":
        return RouteDecision("review", 1, "SNIFF only, needs a second route")
    if sniff_flag or heat_unsure:
        return RouteDecision("review", 1 if sniff_flag else 0, "weak or unfamiliar signal, send to review")
    return RouteDecision("clean", 0, "both routes clean")
