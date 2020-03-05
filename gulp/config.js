var config = {
  'applicationPath': './ulapd_ui',
  'sourcePath': './ulapd_ui/assets/src',
  'destinationPath': './ulapd_ui/assets/dist',
  'sassPath': 'scss/*.scss',
  'sassIncludePaths': [
    'node_modules'
  ],
  'localhost': 'localhost:8080',
  'nodePath': [
    'node_modules'
  ]
}

if ('NODE_PATH' in process.env) {
  config['nodePath'].push(process.env.NODE_PATH)
  config['sassIncludePaths'].push(process.env.NODE_PATH)
}

module.exports = config
