# -*- coding: utf-8 -*-
"""KML 解析测试: 命名空间 / MultiGeometry / CDATA / 内环 / 空几何 / SimpleData 字段"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from parse_kml_polygons import parse_kml_text

NS = 'xmlns="http://www.opengis.net/kml/2.2"'


def placemark(fid="1", coords="100.0,30.0 100.1,30.0 100.1,30.1 100.0,30.1",
              extra="<SimpleData name=\"SHI\">某市</SimpleData>"):
    return (f"<Placemark><ExtendedData><SchemaData>"
            f"<SimpleData name=\"FID_1\">{fid}</SimpleData>{extra}"
            f"</SchemaData></ExtendedData><Polygon><outerBoundaryIs>"
            f"<LinearRing><coordinates>{coords}</coordinates></LinearRing>"
            f"</outerBoundaryIs></Polygon></Placemark>")


class TestParseKml(unittest.TestCase):
    def test_basic_with_default_namespace(self):
        mines, skipped = parse_kml_text(f"<kml {NS}><Document>{placemark()}</Document></kml>")
        self.assertEqual(len(mines), 1)
        self.assertEqual(mines[0]["fid"], "1")
        self.assertEqual(mines[0]["bbox"], [100.0, 30.0, 100.1, 30.1])
        self.assertEqual(mines[0]["shi"], "某市")
        self.assertEqual(skipped, [])

    def test_namespace_prefixed_placemark(self):
        # ogr2ogr 某些版本导出 <kml:Placemark>(根节点声明 kml 前缀), 正则方案抓不到
        pm = placemark().replace("<Placemark>", "<kml:Placemark>").replace("</Placemark>", "</kml:Placemark>")
        pm = pm.replace("<Polygon>", "<kml:Polygon>").replace("</Polygon>", "</kml:Polygon>")
        pm = pm.replace("<coordinates>", "<kml:coordinates>").replace("</coordinates>", "</kml:coordinates>")
        doc = (f'<kml xmlns="http://www.opengis.net/kml/2.2" '
               f'xmlns:kml="http://www.opengis.net/kml/2.2"><Document>{pm}</Document></kml>')
        mines, _ = parse_kml_text(doc)
        self.assertEqual(len(mines), 1)
        self.assertEqual(mines[0]["bbox"], [100.0, 30.0, 100.1, 30.1])

    def test_multigeometry_all_polygons_counted(self):
        pm = (f"<Placemark><SimpleData name=\"FID_1\">7</SimpleData><MultiGeometry>"
              f"<Polygon><outerBoundaryIs><LinearRing><coordinates>"
              f"100.0,30.0 100.1,30.0 100.1,30.1 100.0,30.1</coordinates></LinearRing></outerBoundaryIs></Polygon>"
              f"<Polygon><outerBoundaryIs><LinearRing><coordinates>"
              f"102.0,32.0 102.1,32.0 102.1,32.1 102.0,32.1</coordinates></LinearRing></outerBoundaryIs></Polygon>"
              f"</MultiGeometry></Placemark>")
        mines, _ = parse_kml_text(f"<kml {NS}><Document>{pm}</Document></kml>")
        self.assertEqual(mines[0]["bbox"], [100.0, 30.0, 102.1, 32.1])

    def test_inner_ring_does_not_change_bbox(self):
        pm = (f"<Placemark><SimpleData name=\"FID_1\">8</SimpleData><Polygon>"
              f"<outerBoundaryIs><LinearRing><coordinates>"
              f"100.0,30.0 100.1,30.0 100.1,30.1 100.0,30.1</coordinates></LinearRing></outerBoundaryIs>"
              f"<innerBoundaryIs><LinearRing><coordinates>"
              f"100.04,30.04 100.06,30.04 100.06,30.06 100.04,30.06</coordinates></LinearRing></innerBoundaryIs>"
              f"</Polygon></Placemark>")
        mines, _ = parse_kml_text(f"<kml {NS}><Document>{pm}</Document></kml>")
        self.assertEqual(mines[0]["bbox"], [100.0, 30.0, 100.1, 30.1])

    def test_cdata_coordinates(self):
        pm = (f"<Placemark><SimpleData name=\"FID_1\">9</SimpleData>"
              f"<Polygon><outerBoundaryIs><LinearRing><coordinates><![CDATA["
              f"100.0,30.0 100.1,30.0 100.1,30.1 100.0,30.1]]></coordinates>"
              f"</LinearRing></outerBoundaryIs></Polygon></Placemark>")
        mines, _ = parse_kml_text(f"<kml {NS}><Document>{pm}</Document></kml>")
        self.assertEqual(mines[0]["bbox"], [100.0, 30.0, 100.1, 30.1])

    def test_empty_geometry_is_skipped_and_reported(self):
        pm = "<Placemark><SimpleData name=\"FID_1\">10</SimpleData></Placemark>"
        mines, skipped = parse_kml_text(f"<kml {NS}><Document>{placemark()}{pm}</Document></kml>")
        self.assertEqual(len(mines), 1)
        self.assertEqual(skipped, ["10"])

    def test_z_component_ignored(self):
        pm = placemark(coords="100.0,30.0,0 100.1,30.0,0 100.1,30.1,0 100.0,30.1,0")
        mines, _ = parse_kml_text(f"<kml {NS}><Document>{pm}</Document></kml>")
        self.assertEqual(mines[0]["bbox"], [100.0, 30.0, 100.1, 30.1])


if __name__ == "__main__":
    unittest.main()
