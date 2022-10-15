import bpy, os
from bpy_extras.io_utils import ImportHelper
from bpy.props import BoolProperty,EnumProperty,StringProperty
from ..utils import psd

def menu_func_import(self, context):
  self.layout.operator(PSDLAYERSIMPORTER_OT_Importer.bl_idname, text="Import PSD layers as Plane", icon="TEXTURE")


class PSDLAYERSIMPORTER_OT_Importer(bpy.types.Operator, ImportHelper):
  """import all layers in a PSD file as plane"""
  bl_idname = "psdlayersimporter.importer"
  bl_label = "psdlayersImporter"
  bl_description = "PSDファイルを取り込み"
  bl_options = {'REGISTER', 'UNDO'}

  filename_ext = ".psd"

  psdLayerNameEncoding: EnumProperty(items=[
    ('macroman','default',""),
    ('shift_jis','shift_jis',"")
    ],
    default='macroman',
    name='レイヤー名のエンコード'
  )

  def execute(self, context):
    print("PSDLAYERSIMPORTER_OT_Importer")
    print(self.filepath)
    path = os.path.abspath( bpy.path.abspath(self.filepath))
    psd.add_images_from_psd(path, self.psdLayerNameEncoding)
    return {'FINISHED'}
