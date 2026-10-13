import os
import unittest

BASE = os.path.dirname(os.path.dirname(__file__))

class TestAudioPack(unittest.TestCase):
  def test_nueve_temas_incluidos(self):
    carpeta = os.path.join(BASE, "assets", "music", "tracks")
    temas = [nombre for nombre in os.listdir(carpeta) if nombre.endswith(".ogg")]
    self.assertEqual(len(temas), 9)
    self.assertTrue(all(os.path.getsize(os.path.join(carpeta, tema)) > 1000 for tema in temas))

  def test_efectos_de_sonido_incluidos(self):
    carpeta = os.path.join(BASE, "assets", "sounds")
    for nombre in ("click.wav", "pelota.wav", "lobby.wav", "gol.wav"):
      with self.subTest(nombre=nombre):
        self.assertTrue(os.path.exists(os.path.join(carpeta, nombre)))
        self.assertGreater(os.path.getsize(os.path.join(carpeta, nombre)), 1000)

  def test_configuracion_incluye_subcarpetas_de_audio_android(self):
    with open(os.path.join(BASE, "buildozer.spec"), encoding="utf-8") as archivo:
      spec = archivo.read()
    self.assertIn("assets/music/tracks/*", spec)
    self.assertIn("assets/sounds/*", spec)

if __name__ == "__main__":
  unittest.main()
