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
 * #    Builds a VideoWallWidget from its XML definition file.
 * ##############################################################################
 */
package kutch.biff.marvin.widget.widgetbuilder;

import java.util.logging.Logger;

import kutch.biff.marvin.logger.MarvinLogger;
import kutch.biff.marvin.utility.FrameworkNode;
import kutch.biff.marvin.widget.BaseWidget;
import kutch.biff.marvin.widget.VideoWallWidget;

/**
 * @author Board Instrumentation Framework contributors
 */
public class VideoWallWidgetBuilder {
    private final static Logger LOGGER = Logger.getLogger(MarvinLogger.class.getName());

    public static VideoWallWidget Build(FrameworkNode masterNode, String widgetDefFilename) {
        VideoWallWidget _widget = new VideoWallWidget();

        for (FrameworkNode node : masterNode.getChildNodes()) {
            if (BaseWidget.HandleCommonDefinitionFileConfig(_widget, node)) {
                // handled by common config (Height, Width, Position, CSS, etc.)
            } else if (node.getNodeName().equalsIgnoreCase("#comment")) {
                // ignore comments
            } else if (node.getNodeName().equalsIgnoreCase("Stream")) {
                String uri = node.getTextContent();
                if (null == uri || uri.trim().isEmpty()) {
                    LOGGER.severe("VideoWall Widget has a <Stream> with no URI in " + widgetDefFilename);
                    return null;
                }
                String title = node.hasAttribute("Title") ? node.getAttribute("Title") : "";
                _widget.AddStream(uri.trim(), title);
            } else if (node.getNodeName().equalsIgnoreCase("Columns")) {
                _widget.setColumns(parseIntSafe(node.getTextContent(), 0));
            } else if (node.getNodeName().equalsIgnoreCase("NetworkCaching")) {
                _widget.setNetworkCaching(parseIntSafe(node.getTextContent(), 300));
            } else if (node.getNodeName().equalsIgnoreCase("Gap")) {
                _widget.setGap(parseIntSafe(node.getTextContent(), 6));
            } else if (node.getNodeName().equalsIgnoreCase("ShowTitles")) {
                String str = node.getTextContent();
                if (0 == str.compareToIgnoreCase("True")) {
                    _widget.setShowTitles(true);
                } else if (0 == str.compareToIgnoreCase("False")) {
                    _widget.setShowTitles(false);
                } else {
                    LOGGER.severe("Invalid VideoWall Widget Definition. ShowTitles should be True or False, not: "
                            + str);
                    return null;
                }
            } else {
                LOGGER.severe("Unknown VideoWall Widget setting: " + node.getNodeName() + " in "
                        + widgetDefFilename);
                return null;
            }
        }

        if (_widget.getStreamCount() == 0) {
            LOGGER.warning("VideoWall Widget in " + widgetDefFilename + " has no <Stream> entries configured.");
        }

        return _widget;
    }

    private static int parseIntSafe(String value, int defaultValue) {
        if (null == value) {
            return defaultValue;
        }
        try {
            return Integer.parseInt(value.trim());
        } catch (NumberFormatException ex) {
            return defaultValue;
        }
    }
}
