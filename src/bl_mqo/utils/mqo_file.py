import re


class RawData:
    def __init__(self, data):
        self.data = data
        self.seek = 0

    def get_line(self):
        idx = self.data[self.seek:].find(b'\n')
        start = self.seek
        end = self.seek + idx + 1
        self.seek = end

        return self.data[start:end]

    def eof(self):
        return len(self.data) == self.seek


def remove_return(line):
    for c in [b'\r', b'\n']:
        line = line.replace(c, b'')
    return line


class MqoFile:
    class Scene:
        class DirLight:
            def __init__(self):
                self.dir = None
                self.color = None

            def to_str(self, fmt='STDOUT'):
                s = ""
                if fmt == 'MQO_FILE':
                    s += "\t\tlight {\n"
                    s += "\t\t\tdir {:.3f} {:.3f} {:.3f}\n".format(*self.dir)
                    s += "\t\t\tcolor {:.3f} {:.3f} {:.3f}\n".format(*self.color)
                    s += "\t\t}\n"
                return s

            def set_default_params(self):
                self.dir = [0.408, 0.408, 0.816]
                self.color = [1.0, 1.0, 1.0]

        def __init__(self):
            self.pos = None
            self.lookat = None
            self.head = None
            self.pich = None
            self.bank = None
            self.ortho = None
            self.zoom2 = None
            self.amb = None
            self.frontclip = None
            self.backclip = None
            self.dirlights = []

        def to_str(self, fmt='STDOUT'):
            s = ""
            if fmt == 'MQO_FILE':
                s += "Scene {\n"
                if self.pos is not None:
                    s += "\tpos {:.4f} {:.4f} {:.4f}\n".format(*self.pos)
                if self.lookat is not None:
                    s += "\tlookat {:.4f} {:.4f} {:.4f}\n".format(*self.lookat)
                if self.head is not None:
                    s += "\thead {:.4f}\n".format(self.head)
                if self.pich is not None:
                    s += "\tpich {:.4f}\n".format(self.pich)
                if self.bank is not None:
                    s += "\tbank {:.4f}\n".format(self.bank)
                if self.ortho is not None:
                    s += "\tortho {}\n".format(self.ortho)
                if self.zoom2 is not None:
                    s += "\tzoom2 {:.4f}\n".format(self.zoom2)
                if self.amb is not None:
                    s += "\tamb {:.3f} {:.3f} {:.3f}\n".format(*self.amb)
                if self.frontclip is not None:
                    s += "\tfrontclip {:.5f}\n".format(self.frontclip)
                if self.backclip is not None:
                    s += "\tbackclip {}\n".format(self.backclip)
                if len(self.dirlights) > 0:
                    s += "\tdirlight {}".format(len(self.dirlights)) + " {\n"
                    for light in self.dirlights:
                        s += light.to_str(fmt)
                    s += "\t}\n"
                s += "}\n"

            return s

        def set_default_params(self):
            self.pos = [0, 0, 1500]
            self.lookat = [0, 0, 0]
            self.head = -0.5236
            self.pich = 0.5236
            self.bank = 0.0
            self.ortho = 0
            self.zoom2 = 5.0
            self.amb = [0.25, 0.25, 0.25]
            self.frontclip = 225.00002
            self.backclip = 45000
            light = self.DirLight()
            light.set_default_params()
            self.dirlights.append(light)

    class Material:
        def __init__(self):
            self._name = None
            self._shader = None
            self.vertex_color = None
            self.doubles = None
            self.color = None
            self.diffuse = None
            self.ambient = None
            self.emissive = None
            self.specular = None
            self.power = None
            self.reflect = None
            self.refract = None
            self.texture_map = None
            self.alpha_plane_map = None
            self.bump_map = None
            self.projection_type = None
            self.projection_pos = None
            self.projection_scale = None
            self.projection_angle = None

        @property
        def name(self):
            return self._name

        @name.setter
        def name(self, name_):
            self._name = name_

        @property
        def shader(self):
            return self._shader

        @shader.setter
        def shader(self, shader_):
            self._shader = shader_

        def to_str(self, fmt='STDOUT'):
            s = ""
            if fmt == 'MQO_FILE':
                s = "\t\"{}\"".format(self._name)
                if self._shader is not None:
                    s += " shader({})".format(self._shader)
                if self.vertex_color is not None:
                    s += " vcol({})".format(self.vertex_color)
                if self.doubles is not None:
                    s += " dbls({})".format(self.doubles)
                if self.color is not None:
                    s += " col({:.3f} {:.3f} {:.3f} {:.3f})".format(*self.color)
                if self.diffuse is not None:
                    s += " dif({:.3f})".format(self.diffuse)
                if self.ambient is not None:
                    s += " amb({:.3f})".format(self.ambient)
                if self.emissive is not None:
                    s += " emi({:.3f})".format(self.emissive)
                if self.specular is not None:
                    s += " spc({:.3f})".format(self.specular)
                if self.power is not None:
                    s += " power({:.2f})".format(self.power)
                if self.reflect is not None:
                    s += " reflect({:.3f})".format(self.reflect)
                if self.refract is not None:
                    s += " refract({:.3f})".format(self.refract)
                if self.texture_map is not None:
                    s += " tex({})".format(self.texture_map)
                if self.alpha_plane_map is not None:
                    s += " aplane({})".format(self.alpha_plane_map)
                if self.bump_map is not None:
                    s += " bump({})".format(self.bump_map)
                if self.projection_type is not None:
                    s += " proj_type({})".format(self.projection_type)
                if self.projection_pos is not None:
                    s += " proj_pos({:.3f} {:.3f} {:.3f})".format(*self.projection_pos)
                if self.projection_scale is not None:
                    s += " proj_scale({:.3f} {:.3f} {:.3f})".format(*self.projection_scale)
                if self.projection_angle is not None:
                    s += " proj_pos({:.3f} {:.3f} {:.3f})".format(*self.projection_angle)
                s += "\n"

            return s

        def set_default_params(self):
            self._name = "mat1"
            self._shader = 3
            self.vertex_color = None
            self.doubles = None
            self.color = [1.0, 1.0, 1.0, 1.0]
            self.diffuse = 0.8
            self.ambient = 0.6
            self.emissive = 0.0
            self.specular = 0.0
            self.power = 5.0
            self.reflect = None
            self.refract = None
            self.texture_map = None
            self.alpha_plane_map = None
            self.bump_map = None
            self.projection_type = None
            self.projection_pos = None
            self.projection_scale = None
            self.projection_angle = None

    class Object:
        class Face:
            def __init__(self):
                self.ngons = None
                self.vertex_indices = None
                self.material = None
                self.uv_coords = None
                self.colors = None
                self.crs = None

            def to_str(self, fmt='STDOUT'):
                s = ""
                if fmt == 'MQO_FILE':
                    s += "\t\t{}".format(self.ngons)
                    if self.vertex_indices is not None:
                        vert_indices_str = [str(idx) for idx in self.vertex_indices]
                        s += " V({})".format(" ".join(vert_indices_str))
                    if self.material is not None:
                        s += " M({})".format(self.material)
                    if self.uv_coords is not None:
                        coords = [x for uv in self.uv_coords for x in uv]
                        coords_str = ["{:.5f}".format(c) for c in coords]
                        s += " UV({})".format(" ".join(coords_str))
                    if self.colors is not None:
                        colors = ["{}".format(c) for c in self.colors]
                        s += " COL({})".format(" ".join(colors))
                    if self.crs is not None:
                        crs = ["{}".format(c) for c in self.crs]
                        s += " CRS({})".format(" ".join(crs))
                    s += "\n"

                return s

        def __init__(self):
            self.name = None
            self.uid = None
            self.depth = None
            self.folding = None
            self.scale = None
            self.rotation = None
            self.translation = None
            self.patch = None
            self.patch_triangle = None
            self.segment = None
            self.visible = None
            self.locking = None
            self.shading = None
            self.facet = None
            self.color = None
            self.color_type = None
            self.mirror = None
            self.mirror_axis = None
            self.mirror_distance = None
            self.lathe = None
            self.lathe_axis = None
            self.lathe_segment = None
            self.normal_weight = None
            self.vertices = []
            self.faces = []

        def to_str(self, fmt='STDOUT'):
            s = ""

            if fmt == 'MQO_FILE':
                s += "Object \"{}\"".format(self.name) + " {\n"
                if self.uid is not None:
                    s += "\tuid {}\n".format(self.uid)
                if self.depth is not None:
                    s += "\tdepth {}\n".format(self.depth)
                if self.folding is not None:
                    s += "\tfolding {}\n".format(self.folding)
                if self.scale is not None:
                    s += "\tscale {:.6f} {:.6f} {:.6f}\n".format(*self.scale)
                if self.rotation is not None:
                    s += "\trotation {:.6f} {:.6f} {:.6f}\n".format(*self.rotation)
                if self.translation is not None:
                    s += "\ttranslation {:.6f} {:.6f} {:.6f}\n".format(*self.translation)
                if self.patch is not None:
                    s += "\tpatch {}\n".format(self.patch)
                if self.patch_triangle is not None:
                    s += "\tpatchtri {}\n".format(self.patch_triangle)
                if self.segment is not None:
                    s += "\tsegment {}\n".format(self.segment)
                if self.visible is not None:
                    s += "\tvisible {}\n".format(self.visible)
                if self.locking is not None:
                    s += "\tlocking {}\n".format(self.locking)
                if self.shading is not None:
                    s += "\tshading {}\n".format(self.shading)
                if self.facet is not None:
                    s += "\tfacet {:.1f}\n".format(self.facet)
                if self.color is not None:
                    s += "\tcolor {:.3f} {:.3f} {:.3f}\n".format(*self.color)
                if self.color_type is not None:
                    s += "\tcolor_type {}\n".format(self.color_type)
                if self.mirror is not None:
                    s += "\tmirror {}\n".format(self.mirror)
                if self.mirror_axis is not None:
                    s += "\tmirror_axis {}\n".format(self.mirror_axis)
                if self.mirror_distance is not None:
                    s += "\tmirror_dis {:.3f}\n".format(self.mirror_distance)
                if self.lathe is not None:
                    s += "\tlathe {}\n".format(self.lathe)
                if self.lathe_axis is not None:
                    s += "\tlathe_axis {}\n".format(self.lathe_axis)
                if self.lathe_segment is not None:
                    s += "\tlathe_seg {}\n".format(self.lathe_segment)
                if self.normal_weight is not None:
                    s += "\tnormal_weight {}\n".format(self.normal_weight)
                if len(self.vertices) > 0:
                    s += "\tvertex {}".format(len(self.vertices)) + " {\n"
                    for vert in self.vertices:
                        s += "\t\t{:.4f} {:.4f} {:.4f}\n".format(*vert)
                    s += "\t}\n"
                if len(self.faces) > 0:
                    s += "\tface {}".format(len(self.faces)) + " {\n"
                    for face in self.faces:
                        s += face.to_str(fmt)
                    s += "\t}\n"
                s += "}\n"

            return s

        def set_default_params(self):
            self.name = "obj1"
            self.uid = None
            self.depth = 0
            self.folding = 0
            self.scale = [1, 1, 1]
            self.rotation = [0, 0, 0]
            self.translation = [0, 0, 0]
            self.patch = None
            self.patch_triangle = None
            self.segment = None
            self.visible = 15
            self.locking = 0
            self.shading = 1
            self.facet = 59.5
            self.color = [0.898, 0.498, 0.698]
            self.color_type = 0
            self.mirror = None
            self.mirror_axis = None
            self.mirror_distance = None
            self.lathe = None
            self.lathe_axis = None
            self.lathe_segment = None
            self.normal_weight = 1
            self.vertices = []
            self.faces = []

    def __init__(self):
        self.raw = None

        # .mqo data structure
        self._header = None
        self._version = None
        self.format = None
        self.scene = None
        self.materials = []
        self.objects = []

    def __repr__(self):
        s = "Header: {}\n".format(self._header)
        s += "Version: {}\n".format(self._version)

        return s

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, header_):
        self._header = header_

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version_):
        self._version = version_

    def _parse_thumbnail(self, first_line):
        if first_line.find(b"Thumbnail ") == -1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

        while not self.raw.eof():
            line = self.raw.get_line()
            line = remove_return(line)
            line = line.strip()
            if line.find(b"}"):
                return

        raise RuntimeError("Format Error: Failed to parse 'Thumbnail' field")

    def _parse_light(self, first_line):
        if first_line.find(b"light {") == -1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

        def parse(l, rgx):
            r = re.compile(rgx)
            m = r.search(l)
            if not m:
                raise RuntimeError("Failed to parse. (line:{})".format(l))
            return m.groups()

        light = self.Scene.DirLight()
        while not self.raw.eof():
            line = self.raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                return light

            if line.find(b"dir") != -1:
                rgx = b"dir ([0-9\.]+) ([0-9\.]+) ([0-9\.]+)"
                light.dir = [float(s) for s in parse(line, rgx)]
            elif line.find(b"color") != -1:
                rgx = b"color ([0-9\.]+) ([0-9\.]+) ([0-9\.]+)"
                light.color = [float(s) for s in parse(line, rgx)]

        raise RuntimeError("Format Error: Failed to parse 'light' field")

    def _parse_dirlights(self, first_line):
        r = re.compile(b"dirlights ([0-9]+) {")
        m = r.search(first_line)
        if not m or len(m.groups()) != 1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))
        num_light = int(m.group(1))

        lights = []
        while not self.raw.eof():
            line = self.raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                if len(lights) != num_light:
                    raise RuntimeError("Incorrect number of lights. (expects {} but {})".format(num_light, len(lights)))
                return lights

            if line.find(b"light") != -1:
                lights.append(self._parse_light(line))

        raise RuntimeError("Format Error: Failed to parse 'dirlights' field")

    def _parse_scene(self, first_line):
        if first_line.find(b"Scene {") == -1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

        def parse(l, rgx):
            r = re.compile(rgx)
            m = r.search(l)
            if not m:
                raise RuntimeError("Failed to parse. (line:{})".format(l))
            return m.groups()

        scene = self.Scene()
        while not self.raw.eof():
            line = self.raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                return scene

            if line.find(b"pos") != -1:
                rgx = b"pos ([-0-9\.]+) ([-0-9\.]+) ([-0-9\.]+)"
                scene.pos = [float(s) for s in parse(line, rgx)]
            elif line.find(b"lookat") != -1:
                rgx = b"lookat ([-0-9\.]+) ([-0-9\.]+) ([-0-9\.]+)"
                scene.lookat = [float(s) for s in parse(line, rgx)]
            elif line.find(b"head") != -1:
                rgx = b"head ([-0-9\.]+)"
                scene.head = float(parse(line, rgx)[0])
            elif line.find(b"pich") != -1:
                rgx = b"pich ([-0-9\.]+)"
                scene.pich = float(parse(line, rgx)[0])
            elif line.find(b"bank") != -1:
                rgx = b"bank ([-0-9\.]+)"
                scene.bank = float(parse(line, rgx)[0])
            elif line.find(b"ortho") != -1:
                rgx = b"ortho ([0-9\.]+)"
                scene.ortho = float(parse(line, rgx)[0])
            elif line.find(b"zoom2") != -1:
                rgx = b"zoom2 ([0-9\.]+)"
                scene.zoom2 = float(parse(line, rgx)[0])
            elif line.find(b"amb") != -1:
                rgx = b"amb ([0-9\.]+) ([0-9\.]+) ([0-9\.]+)"
                scene.amb = [float(s) for s in parse(line, rgx)]
            elif line.find(b"frontclip") != -1:
                rgx = b"frontclip ([0-9\.]+)"
                scene.frontclip = float(parse(line, rgx)[0])
            elif line.find(b"backclip") != -1:
                rgx = b"backclip ([0-9\.]+)"
                scene.backclip = float(parse(line, rgx)[0])
            elif line.find(b"dirlights") != -1:
                scene.dirlights = self._parse_dirlights(line)

        raise RuntimeError("Format Error: Failed to parse 'Scene' field.")

    def _parse_material(self, first_line):
        r = re.compile(b"Material ([0-9]+) {")
        m = r.search(first_line)
        if not m or len(m.groups()) != 1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))
        num_mtrl = int(m.group(1))

        def parse(l, rgx):
            r = re.compile(rgx)
            m = r.search(l)
            if not m:
                return None
            return m.groups()

        mtrls = []
        while not self.raw.eof():
            line = self.raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                if num_mtrl != len(mtrls):
                    raise RuntimeError("Incorrect number of materials. (expects {} but {})"
                                       .format(num_mtrl, len(mtrls)))
                return mtrls

            mtrl = self.Material()

            pattern = b"\"([^\"]*)\""
            r = re.compile(pattern)
            m = r.search(line)
            if not m:
                raise RuntimeError("Failed to find material name. (line:{})".format(line))
            try:
                mtrl.name = m.group(1).decode('utf-8')
            except UnicodeDecodeError:
                mtrl.name = m.group(1)

            result = parse(line, b"\"[^\"]*\" .*shader\(([0-4])\)")
            if result:
                mtrl.shader = int(result[0])
            result = parse(line, b"\"[^\"]*\" .*vcol\(([0-1])\)")
            if result:
                mtrl.vertex_color = int(result[0])
            result = parse(line, b"\"[^\"]*\" .*dbls\(([0-1])\)")
            if result:
                mtrl.doubles = int(result[0])
            result = parse(line, b"\"[^\"]*\" .*col\(([0-1]\.[0-9]+) ([0-1]\.[0-9]+) ([0-1]\.[0-9]+) ([0-1]\.[0-9]+)\)")
            if result:
                mtrl.color = [float(v) for v in result]
            result = parse(line, b"\"[^\"]*\" .*dif\(([0-1]\.[0-9]+)\)")
            if result:
                mtrl.diffuse = float(result[0])
            result = parse(line, b"\"[^\"]*\" .*amb\(([0-1]\.[0-9]+)\)")
            if result:
                mtrl.ambient = float(result[0])
            result = parse(line, b"\"[^\"]*\" .*emi\(([0-1]\.[0-9]+)\)")
            if result:
                mtrl.emissive = float(result[0])
            result = parse(line, b"\"[^\"]*\" .*spc\(([0-1]\.[0-9]+)\)")
            if result:
                mtrl.specular = float(result[0])
            result = parse(line, b"\"[^\"]*\" .*power\(([0-9]+\.[0-9]+)\)")
            if result:
                mtrl.power = float(result[0])
            result = parse(line, b"\"[^\"]*\" .*reflect\(([0-1]\.[0-9]+)\)")
            if result:
                mtrl.reflect = float(result[0])
            result = parse(line, b"\"[^\"]*\" .*refract\(([1-5]\.[0-9]+)\)")
            if result:
                mtrl.refract = float(result[0])
            result = parse(line, b"\"[^\"]*\" .*tex\([^\)+]\)")
            if result:
                mtrl.texture_map = result[0].decode('utf-8')
            result = parse(line, b"\"[^\"]*\" .*aplane\([^\)+]\)")
            if result:
                mtrl.alpha_plane_map = result[0].decode('utf-8')
            result = parse(line, b"\"[^\"]*\" .*bump\([^\)+]\)")
            if result:
                mtrl.bump_map = result[0].decode('utf-8')
            result = parse(line, b"\"[^\"]*\" .*proj_type\(([0-3])\)")
            if result:
                mtrl.projection_type = int(result[0])
            result = parse(line, b"\"[^\"]*\" .*proj_pos\((-?[0-9]+\.[0-9]+) (-?[0-9]+\.[0-9]+) (-?[0-9]+\.[0-9]+)")
            if result:
                mtrl.projection_pos = [float(v) for v in result]
            result = parse(line, b"\"[^\"]*\" .*proj_scale\((-?[0-9]+\.[0-9]+) (-?[0-9]+\.[0-9]+) (-?[0-9]+\.[0-9]+)")
            if result:
                mtrl.projection_scale = [float(v) for v in result]
            result = parse(line, b"\"[^\"]*\" .*proj_angle\((-?[0-9]+\.[0-9]+) (-?[0-9]+\.[0-9]+) (-?[0-9]+\.[0-9]+)")
            if result:
                mtrl.projection_angle = [float(v) for v in result]

            mtrls.append(mtrl)

        raise RuntimeError("Format Error: Failed to parse 'Material' field.")

    def _parse_vertex(self, first_line):
        r = re.compile(b"vertex ([0-9]+) {")
        m = r.search(first_line)
        if not m or len(m.groups()) != 1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

        num_verts = int(m.group(1))
        verts = []
        while not self.raw.eof():
            line = self.raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                if num_verts != len(verts):
                    raise RuntimeError("Number of Vertices does not match (expects {}, but {})".format(num_verts, len(verts)))
                return verts

            r = re.compile(b"([-0-9\.]+) ([-0-9\.]+) ([-0-9\.]+)")
            m = r.search(line)
            if not m or len(m.groups()) != 3:
                raise RuntimeError("Invalid format. (line:{})".format(line))

            verts.append([float(elm) for elm in m.groups()])

        raise RuntimeError("Format Error: Failed to parse 'vertex' field.")

    def _parse_face(self, first_line):
        r = re.compile(b"face ([0-9]+) {")
        m = r.search(first_line)
        if not m or len(m.groups()) != 1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

        def parse(l, rgx):
            r = re.compile(rgx)
            m = r.search(l)
            if not m:
                return None
            return m.groups()

        num_faces = int(m.group(1))
        faces = []
        while not self.raw.eof():
            line = self.raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                if num_faces != len(faces):
                    raise RuntimeError("Number of Faces does not match (expects {}, but {})".format(num_faces, len(faces)))
                return faces

            pattern = b"([0-9]+)"
            r = re.compile(pattern)
            m = r.search(line)
            if not m:
                raise RuntimeError("Failed to find material name. (line:{})".format(line))

            face = self.Object.Face()
            face.ngons = int(m.group(1))

            result = parse(line, b"[0-9]+.* V\(([-0-9\. ]+)\)")
            if result:
                face.vertex_indices = [int(vidx) for vidx in result[0].decode("utf-8").split(" ")]
                if face.ngons != len(face.vertex_indices):
                    raise RuntimeError("Number of Vertices does not match (expects {}, but {}".format(face.ngons, len(face.vertex_indices)))

            result = parse(line, b"[0-9]+.* M\(([0-9 ]+)\)")
            if result:
                face.material = int(result[0])

            result = parse(line, b"[0-9]+.* UV\(([0-9\. ]+)\)")
            if result:
                uvs = [float(c) for c in result[0].decode("utf-8").split(" ")]
                face.uv_coords = [[u, v] for u, v in zip(uvs[::2], uvs[1::2])]
                if face.ngons != len(face.uv_coords):
                    raise RuntimeError("Number of UV Coords does not match (expects {}, but {}".format(face.ngons, len(face.uv_coords)))

            result = parse(line, b"[0-9]+.* COL\(([0-9 ]+)\)")
            if result:
                face.colors = [int(c) for c in result[0].split(" ")]
                if face.ngons != len(face.colors):
                    raise RuntimeError("Number of Colors does not match (expects {}, but {}".format(face.ngons, len(face.colors)))

            result = parse(line, b"[0-9]+.* CRS\(([0-9\. ]+)\)")
            if result:
                face.crs = [float(c) for c in result[0].split(" ")]
                if face.ngons != len(face.crs):
                    raise RuntimeError("Number of CRS does not match (expects {}, but {}".format(face.ngons, len(face.crs)))

            faces.append(face)

        raise RuntimeError("Format Error: Failed to parse 'face' field.")

    def _parse_object(self, first_line):
        r = re.compile(b"Object \"([^\"]+)\" {")
        m = r.search(first_line)
        if not m or len(m.groups()) != 1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

        def parse(l, rgx):
            r = re.compile(rgx)
            m = r.search(l)
            if not m:
                raise RuntimeError("Failed to parse. (line:{})".format(l))
            return m.groups()

        obj = self.Object()
        obj.name = m.group(1).decode("utf-8")
        while not self.raw.eof():
            line = self.raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                return obj

            if line.find(b"uid ") != -1:
                rgx = b"uid ([0-9]+)"
                obj.uid = int(parse(line, rgx)[0])
            elif line.find(b"depth ") != -1:
                rgx = b"depth ([0-9]+)"
                obj.depth = int(parse(line, rgx)[0])
            elif line.find(b"folding ") != -1:
                rgx = b"folding ([0-1])"
                obj.folding = int(parse(line, rgx)[0])
            elif line.find(b"scale ") != -1:
                rgx = b"scale ([0-9\.]+) ([0-9\.]+) ([0-9\.]+)"
                obj.scale = [float(v) for v in parse(line, rgx)]
            elif line.find(b"rotation ") != -1:
                rgx = b"rotation ([0-9\.]+) ([0-9\.]+) ([0-9\.]+)"
                obj.rotation = [float(v) for v in parse(line, rgx)]
            elif line.find(b"translation ") != -1:
                rgx = b"translation ([-0-9\.]+) ([-0-9\.]+) ([-0-9\.]+)"
                obj.translation = [float(v) for v in parse(line, rgx)]
            elif line.find(b"patch ") != -1:
                rgx = b"patch ([0-4])"
                obj.patch = int(parse(line, rgx)[0])
            elif line.find(b"patchtri ") != -1:
                rgx = b"patchtri ([0-1])"
                obj.patch_triangle = int(parse(line, rgx)[0])
            elif line.find(b"segment ") != -1:
                rgx = b"segment ([0-9]+)"
                obj.segment = int(parse(line, rgx)[0])
            elif line.find(b"visible ") != -1:
                rgx = b"visible ([0-9]+)"
                obj.visible = int(parse(line, rgx)[0])
            elif line.find(b"locking ") != -1:
                rgx = b"locking ([0-1])"
                obj.locking = int(parse(line, rgx)[0])
            elif line.find(b"shading ") != -1:
                rgx = b"shading ([0-1])"
                obj.shading = int(parse(line, rgx)[0])
            elif line.find(b"facet ") != -1:
                rgx = b"facet ([0-9\.]+)"
                obj.facet = float(parse(line, rgx)[0])
            elif line.find(b"color ") != -1:
                rgx = b"color ([0-9\.]+) ([0-9\.]+) ([0-9\.]+)"
                obj.color = [float(v) for v in parse(line, rgx)]
            elif line.find(b"color_type ") != -1:
                rgx = b"color_type ([0-1])"
                obj.color_type = int(parse(line, rgx)[0])
            elif line.find(b"mirror ") != -1:
                rgx = b"mirror ([0-2])"
                obj.mirror = int(parse(line, rgx)[0])
            elif line.find(b"mirror_axis ") != -1:
                rgx = b"mirror_axis ([0-4])"
                obj.mirror_axis = int(parse(line, rgx)[0])
            elif line.find(b"mirror_dis ") != -1:
                rgx = b"mirror_dis ([0-9\.]+)"
                obj.mirror_distance = float(parse(line, rgx)[0])
            elif line.find(b"lathe ") != -1:
                rgx = b"lathe ([0-3])"
                obj.lathe = int(parse(line, rgx)[0])
            elif line.find(b"lathe_axis ") != -1:
                rgx = b"lathe_axis ([0-2])"
                obj.lathe_axis = int(parse(line, rgx)[0])
            elif line.find(b"lathe_seg ") != -1:
                rgx = b"lathe_seg ([0-9]+)"
                obj.lathe_segment = int(parse(line, rgx)[0])
            elif line.find(b"vertex ") != -1:
                obj.vertices = self._parse_vertex(line)
            elif line.find(b"BVertex ") != -1:
                raise RuntimeError("BVertex is not supported.")
            elif line.find(b"face ") != -1:
                obj.faces = self._parse_face(line)
            elif line.find(b"normal_weight ") != -1:
                rgx = b"normal_weight ([0-9\.]+)"
                obj.normal_weight = float(parse(line, rgx)[0])
            elif line.find(b"vertexattr ") != -1:
                raise RuntimeError("vertexattr is not supported.")

        raise RuntimeError("Format Error: Failed to parse 'Object' field.")

    def get_objects(self):
        return self.objects

    def get_materials(self):
        return self.materials

    def _parse_header(self, line):
        if line != b"Metasequoia Document":
            raise RuntimeError("Header 'Metasequoia Document' is not found.")
        return line.decode('utf-8')

    def _parse_format_and_version(self, line):
        pattern = b"Format (Text|Compress) Ver ([0-9]+\.[0-9]+)"
        r = re.compile(pattern)
        m = r.search(line)
        if not m or len(m.groups()) != 2:
            raise RuntimeError("Format/Version is not found.")

        format = m.group(1).decode('utf-8')
        version = float(m.group(2))
        return format, version

    def _parse_trial_noise(self, first_line):
        if first_line.find(b"TrialNoise") == -1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

    def _parse_include_xml(self, first_line):
        pattern = b"IncludeXml \".+\""
        r = re.compile(pattern)
        m = r.search(first_line)
        if not m or len(m.groups()) != 1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))
        return m.group(1).decode('utf-8')

    def load(self, filepath):
        with open(filepath, "rb") as f:
            self.raw = RawData(f.read())

        while not self.raw.eof():
            line = self.raw.get_line()
            line = remove_return(line)
            line = line.strip()

            # first line must 'Metasequoia Document'
            if not self._header:
                self._header = self._parse_header(line)
                continue

            # second line must 'Format/Version'
            if not self.format or not self._version:
                self.format, self._version = self._parse_format_and_version(line)
                continue

            # TODO: parse 'BlackImage' chunk
            # TODO: parse 'Blob' chunk

            if line.find(b"TrialNoise") != -1:
                self._parse_trial_noise(line)
                raise RuntimeError("The file with TrialNoise chuck is not supported.")
            elif line.find(b"IncludeXml") != -1:
                xml_name = self._parse_include_xml(line)
                print(".xml data '{}' will not be loaded.".format(xml_name))
            elif line.find(b"Thumbnail") != -1:
                self._parse_thumbnail(line)
            elif line.find(b"Scene") != -1:
                self.scene = self._parse_scene(line)
            elif line.find(b"Material") != -1:
                self.materials = self._parse_material(line)
            elif line.find(b"Object") != -1:
                self.objects.append(self._parse_object(line))

    def save(self, filepath):
        s = "Metasequoia Document\n"
        s += "Format {} Ver {}\n".format(self.format, self._version)
        s += "\n"

        s += self.scene.to_str(fmt='MQO_FILE')

        if len(self.materials) > 0:
            s += "Material {}".format(len(self.materials)) + " {\n"
            for mtrl in self.materials:
                s += mtrl.to_str(fmt='MQO_FILE')
            s += "}\n"

        for obj in self.objects:
            s += obj.to_str(fmt='MQO_FILE')

        s += "Eof\n\n"

        with open(filepath, "wb") as f:
            f.write(s.encode('UTF-8'))


def test():
    mqo_file = MqoFile()
    mqo_file.load("./test.mqo")
    mqo_file.save("./clone-test.mqo")

    print(mqo_file)

if __name__ == "__main__":
    test()
