/*
 * ##############################################################################
 * #  Copyright (c) 2026 Board Instrumentation Framework contributors
 * #
 * # Licensed under the Apache License, Version 2.0 (the "License");
 * #  you may not use this file except in compliance with the License.
 * #  You may obtain a copy of the License at
 * #
 * #      http://www.apache.org/licenses/LICENSE-2.0
 * #
 * #  Unless required by applicable law or agreed to in writing, software
 * #  distributed under the License is distributed on an "AS IS" BASIS,
 * #  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * #  See the License for the specific language governing permissions and
 * #  limitations under the License.
 * ##############################################################################
 * #    File Abstract:
 * #    A dynamic N x N video wall widget that displays multiple network video
 * #    streams (UDP/RTP/HLS/HTTP/file) using the native libVLC engine via vlcj.
 * #    Mirrors the standalone scripts/nuc_video_wall.py demo tool, but embeds
 * #    the wall directly inside the Marvin GUI as a single widget.
 * #
 * #    Requires VLC media player (libVLC) to be installed on the host.
 * ##############################################################################
 */
package kutch.biff.marvin.widget;

import java.util.ArrayList;
import java.util.List;

import javafx.collections.ObservableList;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Node;
import javafx.scene.control.Label;
import javafx.scene.image.ImageView;
import javafx.scene.layout.ColumnConstraints;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.Priority;
import javafx.scene.layout.RowConstraints;
import javafx.scene.layout.StackPane;
import kutch.biff.marvin.datamanager.DataManager;

/**
 * Displays up to {@value #MAX_STREAMS} network video streams in an automatically
 * laid-out grid (video wall) inside the Marvin GUI.
 *
 * @author Board Instrumentation Framework contributors
 */
public class VideoWallWidget extends BaseWidget {
    public static final int MAX_STREAMS = 16;

    // Tracks whether native libVLC was located; null until first probed.
    private static Boolean _NativeVlcAvailable = null;

    private final GridPane _wallPane;
    private final List<String> _uris;
    private final List<String> _titles;
    // Opaque handles to the created vlcj media players / factory, retained so
    // they can be released on shutdown. Typed as Object to avoid a hard compile
    // dependency in this field declaration; actual types are resolved lazily.
    private final List<Object> _players;
    private Object _mediaPlayerFactory;

    private int _columns; // 0 == auto (ceil(sqrt(n)))
    private int _networkCaching; // milliseconds of VLC network caching
    private int _gap; // pixel gap between cells
    private boolean _showTitles;

    public VideoWallWidget() {
        _wallPane = new GridPane();
        _uris = new ArrayList<>();
        _titles = new ArrayList<>();
        _players = new ArrayList<>();
        _mediaPlayerFactory = null;
        _columns = 0;
        _networkCaching = 300;
        _gap = 6;
        _showTitles = true;
    }

    public void AddStream(String uri, String title) {
        if (_uris.size() >= MAX_STREAMS) {
            LOGGER.warning("VideoWall supports at most " + MAX_STREAMS + " streams; ignoring: " + uri);
            return;
        }
        _uris.add(uri);
        _titles.add(title);
    }

    public void setColumns(int columns) {
        _columns = columns;
    }

    public void setNetworkCaching(int ms) {
        _networkCaching = ms;
    }

    public void setGap(int gap) {
        _gap = gap;
    }

    public void setShowTitles(boolean show) {
        _showTitles = show;
    }

    public int getStreamCount() {
        return _uris.size();
    }

    @Override
    protected void ConfigureDimentions() {
        if (getWidth() > 0) {
            _wallPane.setPrefWidth(getWidth());
            _wallPane.setMinWidth(getWidth());
        }
        if (getHeight() > 0) {
            _wallPane.setPrefHeight(getHeight());
            _wallPane.setMinHeight(getHeight());
        }
    }

    @Override
    public boolean Create(GridPane pane, DataManager dataMgr) {
        SetParent(pane);
        ConfigureDimentions();
        ConfigureAlignment();
        SetupPeekaboo(dataMgr);

        _wallPane.setHgap(_gap);
        _wallPane.setVgap(_gap);
        _wallPane.setStyle("-fx-background-color: #0d1117;");

        BuildWall();

        pane.add(_wallPane, getColumn(), getRow(), getColumnSpan(), getRowSpan());

        SetupTaskAction();
        return ApplyCSS();
    }

    private void BuildWall() {
        int n = _uris.size();
        if (n == 0) {
            _wallPane.add(MakeMessageCell("No streams configured"), 0, 0);
            return;
        }

        int cols = _columns > 0 ? _columns : (int) Math.ceil(Math.sqrt(n));
        if (cols < 1) {
            cols = 1;
        }
        int rows = (int) Math.ceil((double) n / cols);

        for (int c = 0; c < cols; c++) {
            ColumnConstraints cc = new ColumnConstraints();
            cc.setPercentWidth(100.0 / cols);
            cc.setHgrow(Priority.ALWAYS);
            cc.setFillWidth(true);
            _wallPane.getColumnConstraints().add(cc);
        }
        for (int r = 0; r < rows; r++) {
            RowConstraints rc = new RowConstraints();
            rc.setPercentHeight(100.0 / rows);
            rc.setVgrow(Priority.ALWAYS);
            rc.setFillHeight(true);
            _wallPane.getRowConstraints().add(rc);
        }

        boolean vlcAvailable = EnsureNativeVlc();

        for (int idx = 0; idx < n; idx++) {
            int row = idx / cols;
            int col = idx % cols;
            String uri = _uris.get(idx);
            String title = _titles.get(idx);
            if (title == null || title.isEmpty()) {
                title = "Stream " + (idx + 1);
            }

            StackPane cell = MakeStreamCell(uri, title, vlcAvailable);
            GridPane.setFillWidth(cell, true);
            GridPane.setFillHeight(cell, true);
            _wallPane.add(cell, col, row);
        }
    }

    private StackPane MakeStreamCell(String uri, String title, boolean vlcAvailable) {
        StackPane holder = new StackPane();
        holder.setStyle("-fx-background-color: black; -fx-border-color: #1f2937; -fx-border-width: 1;");
        holder.setMinSize(0, 0);

        if (!vlcAvailable) {
            holder.getChildren().add(BuildTitleOverlay(
                    new Label("VLC (libVLC) not found - install VLC media player"), title));
            return holder;
        }

        ImageView imageView = new ImageView();
        imageView.setPreserveRatio(true);
        imageView.fitWidthProperty().bind(holder.widthProperty());
        imageView.fitHeightProperty().bind(holder.heightProperty());
        StackPane.setAlignment(imageView, Pos.CENTER);
        holder.getChildren().add(imageView);

        if (_showTitles) {
            Label lbl = new Label(title);
            lbl.setStyle("-fx-text-fill: #e5e7eb; -fx-background-color: rgba(17,24,39,0.65); "
                    + "-fx-padding: 2 8 2 8; -fx-font-size: 11px; -fx-font-weight: bold;");
            StackPane.setAlignment(lbl, Pos.TOP_LEFT);
            StackPane.setMargin(lbl, new Insets(6, 6, 6, 6));
            holder.getChildren().add(lbl);
        }

        StartStream(imageView, uri);
        return holder;
    }

    private Node BuildTitleOverlay(Label body, String title) {
        StackPane inner = new StackPane();
        body.setStyle("-fx-text-fill: #f87171; -fx-font-size: 12px;");
        StackPane.setAlignment(body, Pos.CENTER);
        inner.getChildren().add(body);
        if (_showTitles) {
            Label lbl = new Label(title);
            lbl.setStyle("-fx-text-fill: #9ca3af; -fx-padding: 2 8 2 8; -fx-font-size: 11px; -fx-font-weight: bold;");
            StackPane.setAlignment(lbl, Pos.TOP_LEFT);
            StackPane.setMargin(lbl, new Insets(6, 6, 6, 6));
            inner.getChildren().add(lbl);
        }
        return inner;
    }

    private StackPane MakeMessageCell(String message) {
        StackPane holder = new StackPane();
        holder.setStyle("-fx-background-color: black; -fx-border-color: #1f2937; -fx-border-width: 1;");
        Label lbl = new Label(message);
        lbl.setStyle("-fx-text-fill: #9ca3af; -fx-font-size: 12px;");
        holder.getChildren().add(lbl);
        return holder;
    }

    /**
     * Creates a vlcj embedded media player bound to the given ImageView and
     * begins playback of the stream. Isolated so the vlcj types are only loaded
     * when native libVLC is present.
     */
    private void StartStream(ImageView imageView, String uri) {
        try {
            if (_mediaPlayerFactory == null) {
                // Create libVLC quietly: the VideoWall renders into off-screen
                // JavaFX callback surfaces, so native video-output features like
                // "always on top" don't apply and only produce log noise.
                //   --quiet             : suppress libVLC info/error console spam
                //   --no-video-title-show : never overlay the media title
                //   --no-video-on-top   : don't try to force the vout on top
                _mediaPlayerFactory = new uk.co.caprica.vlcj.factory.MediaPlayerFactory(
                        "--quiet",
                        "--no-video-title-show",
                        "--no-video-on-top");
            }
            uk.co.caprica.vlcj.factory.MediaPlayerFactory factory =
                    (uk.co.caprica.vlcj.factory.MediaPlayerFactory) _mediaPlayerFactory;

            uk.co.caprica.vlcj.player.embedded.EmbeddedMediaPlayer player =
                    factory.mediaPlayers().newEmbeddedMediaPlayer();
            player.videoSurface().set(
                    new uk.co.caprica.vlcj.javafx.videosurface.ImageViewVideoSurface(imageView));

            _players.add(player);

            final String mrl = uri;
            final String cacheOpt = ":network-caching=" + _networkCaching;
            // Kick off playback off the JavaFX thread to avoid blocking the UI
            // while VLC opens the network stream.
            new Thread(() -> player.media().play(mrl, cacheOpt, ":no-video-title-show"),
                    "VideoWall-Start").start();
        } catch (Throwable ex) {
            LOGGER.severe("VideoWall failed to start stream '" + uri + "': " + ex.getMessage());
        }
    }

    private static synchronized boolean EnsureNativeVlc() {
        if (_NativeVlcAvailable == null) {
            try {
                _NativeVlcAvailable = new uk.co.caprica.vlcj.factory.discovery.NativeDiscovery().discover();
                if (!_NativeVlcAvailable) {
                    LOGGER.warning("VideoWall: native libVLC not found. Install VLC media player "
                            + "so the video wall can decode streams.");
                }
            } catch (Throwable ex) {
                LOGGER.severe("VideoWall: error probing for native libVLC: " + ex.getMessage());
                _NativeVlcAvailable = false;
            }
        }
        return _NativeVlcAvailable;
    }

    @Override
    public void PrepareForAppShutdown() {
        for (Object obj : _players) {
            try {
                uk.co.caprica.vlcj.player.embedded.EmbeddedMediaPlayer player =
                        (uk.co.caprica.vlcj.player.embedded.EmbeddedMediaPlayer) obj;
                player.controls().stop();
                player.release();
            } catch (Throwable ex) {
                // best effort cleanup
            }
        }
        _players.clear();
        if (_mediaPlayerFactory != null) {
            try {
                ((uk.co.caprica.vlcj.factory.MediaPlayerFactory) _mediaPlayerFactory).release();
            } catch (Throwable ex) {
                // best effort cleanup
            }
            _mediaPlayerFactory = null;
        }
    }

    @Override
    public Node getStylableObject() {
        return _wallPane;
    }

    @Override
    public ObservableList<String> getStylesheets() {
        return _wallPane.getStylesheets();
    }

    @Override
    public void UpdateTitle(String strTitle) {
        LOGGER.warning("Tried to update Title of a VideoWallWidget to " + strTitle);
    }

    static void ResetNativeProbeForTesting() {
        _NativeVlcAvailable = null;
    }
}
