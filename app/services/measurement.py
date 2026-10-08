from pathlib import Path
import tempfile
import zipfile

import geopandas as gpd
from shapely.geometry import mapping

from app.config import MAX_UNZIPPED_SIZE


class GeospatialProcessingError(ValueError):
    pass


def _safe_extract(zip_path: Path, target: Path):
    total = 0
    root = target.resolve()
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            total += info.file_size
            if total > MAX_UNZIPPED_SIZE:
                raise GeospatialProcessingError("Uncompressed ZIP size exceeds limit.")
            destination = (target / info.filename).resolve()
            if root not in destination.parents:
                raise GeospatialProcessingError("Unsafe ZIP entry detected.")
        z.extractall(target)


def _read_source(path: Path) -> gpd.GeoDataFrame:
    suffix = path.suffix.lower()
    if suffix in {".geojson", ".json", ".kml"}:
        return gpd.read_file(path)
    if suffix == ".kmz":
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(path) as z:
                names = [n for n in z.namelist() if n.lower().endswith(".kml")]
                if not names:
                    raise GeospatialProcessingError("KMZ does not contain a KML file.")
                z.extract(names[0], tmp)
                return gpd.read_file(Path(tmp) / names[0])
    if suffix == ".zip":
        with tempfile.TemporaryDirectory() as tmp:
            _safe_extract(path, Path(tmp))
            shp = next(Path(tmp).rglob("*.shp"), None)
            if not shp:
                raise GeospatialProcessingError("ZIP does not contain a Shapefile (.shp).")
            return gpd.read_file(shp)
    raise GeospatialProcessingError(f"Unsupported file type: {suffix}")


def _metric_crs(gdf: gpd.GeoDataFrame):
    if gdf.crs is None:
        raise GeospatialProcessingError("Input data has no CRS.")
    if gdf.crs.is_projected:
        return gdf.crs
    try:
        return gdf.estimate_utm_crs()
    except Exception as exc:
        raise GeospatialProcessingError("Unable to determine a projected CRS.") from exc


def _measure_geometry(geom, projected_geom):
    if geom is None or geom.is_empty:
        return {"type": geom.geom_type if geom is not None else None,
                "length_m": 0.0, "area_m2": 0.0}

    gtype = geom.geom_type
    if gtype in {"Polygon", "MultiPolygon"}:
        return {"type": gtype, "length_m": float(projected_geom.length),
                "area_m2": float(projected_geom.area)}
    if gtype in {"LineString", "MultiLineString"}:
        return {"type": gtype, "length_m": float(projected_geom.length),
                "area_m2": 0.0}
    if gtype in {"Point", "MultiPoint"}:
        return {"type": gtype, "length_m": 0.0, "area_m2": 0.0}
    return {"type": gtype, "length_m": float(projected_geom.length),
            "area_m2": float(projected_geom.area)}


def process_file(path: Path):
    gdf = _read_source(path)
    if gdf.empty:
        return {"crs": str(gdf.crs) if gdf.crs else None,
                "measurement_crs": None, "feature_count": 0, "features": []}

    metric_crs = _metric_crs(gdf)
    projected = gdf.to_crs(metric_crs)

    features = []
    for (_, row), (_, prow) in zip(gdf.iterrows(), projected.iterrows()):
        result = _measure_geometry(row.geometry, prow.geometry)
        props = {}
        for key, value in row.drop(labels=["geometry"]).items():
            if hasattr(value, "item"):
                value = value.item()
            if value is not None and not isinstance(value, (str, int, float, bool, list, dict)):
                value = str(value)
            props[str(key)] = value
        result["properties"] = props
        result["geometry"] = mapping(row.geometry)
        features.append(result)

    return {
        "crs": str(gdf.crs),
        "measurement_crs": str(metric_crs),
        "feature_count": len(features),
        "features": features,
    }
