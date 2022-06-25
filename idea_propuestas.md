# Cliente side

- Cada torrent cliente responde a un **.torrent** distinto
- Cada vez que cargo un **.torrent** se va a crear una instancia separada de
  TorrentClient para manejarlo a el por un thread distinto de esta forma se 
  permite que esten varios .torrent a la vez descargandose
