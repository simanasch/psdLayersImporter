'''
Copyright (C) 2022 simana
tktossi@live.com

Created by simana

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
  "name": "psd Layers Importer",
  "author": "simana",
  "version": (0, 0, 1),
  "blender": (2, 93, 3),
  "location": "Object",
  "description": "import all layers in a PSD file as plane",
  "warning": "",
  "support": "TESTING",
  "doc_url": "",
  "tracker_url": "",
  "category": "Object",
}

# "reload Script"でスクリプトを再読み込みした場合に関連ファイルを再読み込みする
if "bpy" in locals():
  from . import auto_load
  auto_load.reload()

import bpy
try:
  import psd_tools
except ModuleNotFoundError:
  # psd-toolがインポートされていない場合はインストールしてmodule再読み込み
  print("psd-tool not installed, installing...")
  import sys,subprocess
  subprocess.call([sys.executable, '-m','pip', 'install', 'psd-tools' ])
except Exception as e:
  # subprocessが落ちたらエラー出力
  import logging
  logging.error(e);

from . import auto_load
auto_load.init()

#
# アドオン有効化時の処理
#
def register():
  auto_load.register()

  # from .classes.psdSettings import psd_OT_Settings
  from .operator.importer import menu_func_import
  # from .handler.handler import onFrameChangePost
  # bpy.types.Object.psd_settings = bpy.props.PointerProperty(type=psd_OT_Settings)
  bpy.types.VIEW3D_MT_image_add.append(menu_func_import)
  # # 既にインスタンス追加していた場合、インスタンス削除
  # try:
  #   index = bpy.app.handlers.frame_change_post.index(onFrameChangePost)
  #   bpy.app.handlers.frame_change_post.remove(index)
  #   print("layeredPsdMaterial remove handler")
  # except ValueError:
  #   print("layeredPsdMaterial handler not exists")
  #   pass
  # # 
  # bpy.app.handlers.frame_change_post.append(onFrameChangePost)

#
# アドオン無効化時の処理
# 
def unregister():
  auto_load.unregister()
  # from .handler.handler import onFrameChangePost
  # from .operator.operator import menu_func_import
  # from .handler.handler import onFrameChangePost
  # bpy.app.handlers.frame_change_post.remove(onFrameChangePost)
  # bpy.types.VIEW3D_MT_image_add.remove(menu_func_import)
