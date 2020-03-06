from xml.etree import ElementTree


def kml_simplify(kml):
    doc = ElementTree.fromstring(kml)
    result = []
    ns = { 'kml': 'http://www.opengis.net/kml/2.2' }

    for p in doc.findall('.//kml:Placemark', ns):
        media = p.find('.//kml:Data[@name="gx_media_links"]/kml:value', ns)
        media = media.text.strip().split(' ') if media is not None else []

        result.append({
            'name': p.find('.//kml:name', ns).text.strip(),
            'coordinates': p.find('.//kml:coordinates', ns).text.strip(),
            'media': media
        })

    return result


def kml_diff(current, before):
    added = []
    updated = []
    removed = []

    for a in before:
        if next(filter(lambda b: a['coordinates'] == b['coordinates'], current), None) is None:
            removed.append(a)

    for a in current:
        item = next(filter(lambda b: a['coordinates'] == b['coordinates'], before), None)

        if item is None:
            added.append(a)
        elif a['name'] != item['name'] or (len(item['media']) == 0 and len(a['media']) > 0):
            updated.append(a)

    return {
        'added': added,
        'updated': updated,
        'removed': removed
    }