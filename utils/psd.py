import numpy as np, os, re
import bpy
from psd_tools import PSDImage
from PIL import Image

# やること
# layer構造を返す
# PIL.imageを返す
# pixel/mのレート
pixel_rate = 0.0
zIndex=0.00
cacheFolder=""

def get_file_name_from_path(filepath):
  return os.path.splitext( os.path.basename(filepath))[0]

def get_project_folder():
  return bpy.path.abspath("//")

def get_image_as_np_array(image):
  return np.array(image).flatten() / 255

def sanitizeFilePath(path):
  return re.sub(r"[\/:*?\"<>|]","_",path )

def get_layer_absolute_path(layer):
  print(layer.parent)
  if layer.parent == None:
    return "Root"
  layerName=re.sub(r"[\/:*?\"<>|]","_",layer.name )
  if layer.parent.kind == "group":
    return os.path.join(get_layer_absolute_path(layer.parent), layerName)
  else:
    return layerName

def add_images_from_psd(path, encoding='macroman',cacheImage=False):
  # psdファイルを開く
  psd = PSDImage.open(os.path.abspath(path),encoding=encoding)
  if cacheImage:
    # layer画像のキャッシュを生成する場合、キャッシュの格納先フォルダを作る
    global cacheFolder
    cacheFolder = os.path.join( get_project_folder(),get_file_name_from_path(os.path.abspath(path)))
    os.makedirs(cacheFolder,exist_ok=True)
  rootPlane = add_group_layer(psd)
  rootPlane.name = get_file_name_from_path(path)
  parentNames = {"Root":rootPlane}

  # psd.descendantsでループ
  for layer in list(psd.descendants()):
    print(get_layer_absolute_path(layer))
    # pixelLayerなら、平面を追加
    if layer.kind == 'pixel':
      layerPlane = add_plane_of_layer_size(layer, psd, cacheImage)
      if layer.parent.name == 'Root':
        global zIndex
        zIndex += 0.0001
    # groupならemptyObjectを追加、parentにする
    elif layer.kind=='group':
      layerPlane = add_group_layer(layer)
      parentNames[get_layer_absolute_path(layer)] = layerPlane
      if cacheImage == True:
        os.makedirs(os.path.join(cacheFolder,get_layer_absolute_path(layer)), exist_ok=True)
    layerPlane.parent = parentNames[get_layer_absolute_path(layer.parent)]


def add_group_layer(psd):
  global pixel_rate
  global zIndex
  zIndex += 0.0001
  if pixel_rate == 0.0:
    # 1pxあたり何メートルになるか出す
    pixel_rate = 1/max(psd.size)
  w, h = psd.size
  bpy.ops.object.empty_add(type='IMAGE', align='WORLD', location=(0, 0, zIndex), scale=(w * pixel_rate, h * pixel_rate,0))
  obj = bpy.context.object
  obj.name = psd.name
  return obj

def add_plane_of_layer_size(psdLayer, root=None, cacheImage=False):
  global pixel_rate
  # Rootになるオブジェクトを追加、object名=ファイル名
  bpy.ops.mesh.primitive_plane_add()
  obj = bpy.context.object
  obj.name = psdLayer.name
  w, h = psdLayer.size
  ow,oh = psdLayer.offset
  # importするpsdファイルに合わせ、オブジェクトをリサイズする
  bpy.ops.transform.resize(value=((w*pixel_rate, h*pixel_rate,0)))
  # materialを設定
  obj.active_material = add_material(psdLayer,cacheImage)
  # 可視性を設定する
  layerVisibility = get_layer_visibility(psdLayer)
  obj.hide_viewport = layerVisibility
  obj.hide_render = layerVisibility
  if root is not None:
    rw,rh = root.size
    obj.location = (((ow+w/2)-rw/2) * pixel_rate*2, ((oh+h/2)-rh/2) * pixel_rate*2, zIndex)
    if cacheImage:
      obj.location[1] = obj.location[1] * -1
  return obj

def get_layer_visibility(psdLayer):
  return not(psdLayer.name.startswith('!') | psdLayer.is_visible())

def add_material(psdLayer,cacheImage=False):
  # マテリアルを新規追加
  add_mat = bpy.data.materials.new(psdLayer.name)
  w, h = psdLayer.size
  add_mat.use_fake_user = True
  # 透過を設定
  add_mat.blend_method = 'CLIP'
  add_mat.shadow_method = 'CLIP'
  add_mat.use_nodes = True

  # ノードを追加
  shader_node = add_mat.node_tree.nodes['Principled BSDF']
  # 裏表で明度が変わるのを避けるため、メタリックの値を1にする
  # shader_node.inputs['Metallic'].default_value=1.0
  imageTextureNode = add_mat.node_tree.nodes.new("ShaderNodeTexImage")

  # ノード同士のリンクを設定
  add_mat.node_tree.links.new(shader_node.inputs['Base Color'], imageTextureNode.outputs['Color'])
  add_mat.node_tree.links.new(shader_node.inputs['Alpha'], imageTextureNode.outputs['Alpha'])
  # 表示画像を設定
  if cacheImage:
    global cacheFolder
    layerName = sanitizeFilePath(psdLayer.name)
    cachePath = os.path.join(cacheFolder , get_layer_absolute_path(psdLayer) + ".png")
    psdLayer.topil().save(cachePath)
    print(cachePath)
    print(layerName)
    bpy_image = bpy.data.images.new(layerName, w, h, alpha=True)
    bpy_image.filepath = cachePath
    bpy_image.source = "FILE"
    bpy_image.reload()
    imageTextureNode.image = bpy_image
  else:
    bpy_image = bpy.data.images.new(psdLayer.name, w, h, alpha=True)
    bpy_image.pack()
    bpy_image.use_fake_user = True
    bpy_image.pixels = psdLayer.numpy().flatten()
    imageTextureNode.image = bpy_image
  return add_mat
