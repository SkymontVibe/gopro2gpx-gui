# gopro2gpx-gui

## Prebuilt `ffmpeg` for Windows

Used `mingw-w64` build from [nuwen.net](https://nuwen.net/mingw.html). Add `C:\MinGW\bin` to `PATH` environment variable, and place [yasm.exe](http://www.tortall.net/projects/yasm/wiki/Download) there.

```bash
# ffmpeg 7.1 source root dir
./configure --disable-debug \
            --disable-doc \
            --disable-encoders \
            --disable-decoders \
            --disable-hwaccels \
            --disable-muxers \
            --disable-bsfs \
            --disable-protocols \
            --disable-devices \
            --disable-ffplay \
            --disable-filters \
            --disable-demuxers \
            --disable-parsers \
            --enable-demuxer=mov \
            --enable-small \
            --disable-network \
            --disable-mediafoundation \
            --disable-d3d11va \
            --disable-dxva2 \
            --disable-schannel \
            --enable-protocol=file \
            --enable-encoder=rawvideo \
            --enable-muxer=rawvideo \
            --enable-protocol=pipe

make -j8 # wait for a while
make install
```

## Build a single executable file for Windows

```bash
pyinstaller goprogui.spec # generated to the dist/ folder
```