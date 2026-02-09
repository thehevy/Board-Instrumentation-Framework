PS D:\github\Board-Instrumentation-Framework\Marvin> python validate_config.py "D:\Intel Vision 2022\Marvin\IPU_DEMO\IpuDemo.App.fast.xml" -v -a
🔍 Validating Marvin configuration: IpuDemo.App.fast.xml
======================================================================

📑 Tab Structure Analysis:

  📄 Tab: Tab.Thanks
     🔍 Attributes: ID=Tab.Thanks, Width=100%g, Height=100%g, hgap=0, vgap=0, Align=NW, TabTitle=The Team, File=$(AppDir)\Tab.Thanx.xml, Task=SetTab.$(TabTitle)
     📂 External File: $(AppDir)\Tab.Thanx.xml
     📂 Resolved Path: IPU_DEMO\Tab.Thanx.xml
     📂 Adjusted Path: Tab.Thanx.xml
     📂 Full Path: D:\Intel Vision 2022\Marvin\IPU_DEMO\Tab.Thanx.xml
     📂 Exists: True
        📊 Contains:
           • Grids: 6
           • Widgets: 2
           • DynamicGrids: 0
           📁 Referenced Grid Files:
              - $(AppDir)\Header\Grid.Header.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 2
                    • DynamicGrids: 0

  📄 Tab: Tab.Initiator.Generation
     🔍 Attributes: ID=Tab.Initiator.Generation, Width=100%g, Height=100%g, hgap=0, vgap=0, Align=NW, ENABLE_K8s_IPU=True, TabTitle=K8s Comparison, File=$(AppDir)\Tab.InitiatorV2.xml, Task=SetTab.$(TabTitle), NS1=$(ICX-K8S-NS), NS2=$(SPR-K8S-NS), Color1=$(ICX_K8s_COLOR), Color2=$(SPR_K8S_COLOR), Desc1=$(ICX-K8S-DESC), Desc2=$(SPR-K8S-DESC), NUM_RECORDINGS=$(ICX-SPR-RECORDINGS), MAX_GAUGE_VAL=$(ICX-SPR-MAX-VALUE), IMAGE_FOLDER=$(ICX-SPR-IMAGE-FOLDER), WHICH=ICX_SPR, SHOW_DELTA_INDEX=$(ICX-SPR-SHOW-DELTA-INDEX), BANNER=4th Gen Intel Xeon Scalable Processor Improvements, GID_LEFT=$(GAUGE-K8S-ID-LEFT), GID_RIGHT=$(GAUGE-K8S-ID-RIGHT), GAUGE_UNITS=$(GAUGE-K8S-UNITS)
     📂 External File: $(AppDir)\Tab.InitiatorV2.xml
     📂 Resolved Path: IPU_DEMO\Tab.InitiatorV2.xml
     📂 Adjusted Path: Tab.InitiatorV2.xml
     📂 Full Path: D:\Intel Vision 2022\Marvin\IPU_DEMO\Tab.InitiatorV2.xml
     📂 Exists: True
        📊 Contains:
           • Grids: 17
           • Widgets: 28
           • DynamicGrids: 1
           📁 Referenced Grid Files:
              - $(AppDir)\Header\Grid.Header.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 2
                    • DynamicGrids: 0
              - $(AppDir)\Panel.Message.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 1
                    • DynamicGrids: 0
              - $(AppDir)\Panel.Message.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 1
                    • DynamicGrids: 0
              - $(AppDir)\Panel.Message.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 1
                    • DynamicGrids: 0
              - $(AppDir)\Panel.Message.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 1
                    • DynamicGrids: 0
           🔄 DynamicGrid Configurations:
              - ID: unknown

  📄 Tab: Tab.Initiator.IPU
     🔍 Attributes: ID=Tab.Initiator.IPU, Width=100%g, Height=100%g, hgap=0, vgap=0, Align=NW, ENABLE_K8s_IPU=True, TabTitle=Intel IPU E2000, File=$(AppDir)\Tab.InitiatorV2.xml, Task=SetTab.$(TabTitle), NS1=$(SPR-K8S-NS), NS2=$(SPR-IPU-NS), Color1=$(SPR_K8S_COLOR), Color2=$(SPR_IPU_COLOR), Desc1=$(SPR-K8S-DESC), Desc2=$(SPR-IPU-DESC), NUM_RECORDINGS=$(SPR-IPU-RECORDINGS), MAX_GAUGE_VAL=$(SPR-IPU-MAX-VALUE), IMAGE_FOLDER=$(SPR-IPU-IMAGE-FOLDER), WHICH=SPR_IPU, SHOW_DELTA_INDEX=$(SPR-IPU-SHOW-DELTA-INDEX), BANNER=Kubernetes Without Compromise, GID_LEFT=$(GAUGE-K8S-ID-LEFT), GID_RIGHT=$(GAUGE-K8S-ID-RIGHT), GAUGE_UNITS=$(GAUGE-K8S-UNITS)
     📂 External File: $(AppDir)\Tab.InitiatorV2.xml
     📂 Resolved Path: IPU_DEMO\Tab.InitiatorV2.xml
     📂 Adjusted Path: Tab.InitiatorV2.xml
     📂 Full Path: D:\Intel Vision 2022\Marvin\IPU_DEMO\Tab.InitiatorV2.xml
     📂 Exists: True
        📊 Contains:
           • Grids: 17
           • Widgets: 28
           • DynamicGrids: 1
           📁 Referenced Grid Files:
              - $(AppDir)\Header\Grid.Header.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 2
                    • DynamicGrids: 0
              - $(AppDir)\Panel.Message.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 1
                    • DynamicGrids: 0
              - $(AppDir)\Panel.Message.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 1
                    • DynamicGrids: 0
              - $(AppDir)\Panel.Message.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 1
                    • DynamicGrids: 0
              - $(AppDir)\Panel.Message.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 1
                    • DynamicGrids: 0
           🔄 DynamicGrid Configurations:
              - ID: unknown

  📄 Tab: Tab.Initiator.Cloud
     🔍 Attributes: ID=Tab.Initiator.Cloud, Width=100%g, Height=100%g, hgap=0, vgap=0, Align=NW, ENABLE_K8s_IPU=True, TabTitle=Application Device Queues (ADQ), File=$(AppDir)\Tab.InitiatorV3.xml, Task=SetTab.$(TabTitle), NS1=$(GAUGE_NS1), NS2=$(GAUGE_NS1), Color1=$(NON_ADQ_COLOR), Color2=$(ADQ_COLOR), Desc1=$(Baseline-CLOUD-DESC), Desc2=$(ADQ-CLOUD-DESC), NUM_RATES=$(CLOUD-RATES), MAX_GAUGE_VAL=$(CLOUD-TPS-MAX-VALUE), LAT_MAX_GAUGE_VAL=$(CLOUD-LAT-MAX-VALUE), IMAGE_FOLDER=$(ADQ-IMAGE-FOLDER), WHICH=ADQ, SHOW_DELTA_INDEX=$(CLOUD-SHOW-DELTA-INDEX), BANNER=Intel Ethernet 800 Series with Application Device Queues (ADQ), GID_LEFT=$(GAUGE-CLOUD-ID-LEFT), GID_RIGHT_DESC=$(GAUGE-CLOUD-ID-RIGHT-TEXT), GID_LEFT_DESC=$(GAUGE-CLOUD-ID-LEFT-TEXT), GID_RIGHT=$(GAUGE-CLOUD-ID-RIGHT), GID_RIGHT_COLOR=$(GAUGE-CLOUD-ID-RIGHT-COLOR), GID_LEFT_COLOR=$(GAUGE-CLOUD-ID-LEFT-COLOR), GAUGE_UNITS=$(GAUGE-CLOUD-UNITS)
     📂 External File: $(AppDir)\Tab.InitiatorV3.xml
     📂 Resolved Path: IPU_DEMO\Tab.InitiatorV3.xml
     📂 Adjusted Path: Tab.InitiatorV3.xml
     📂 Full Path: D:\Intel Vision 2022\Marvin\IPU_DEMO\Tab.InitiatorV3.xml
     📂 Exists: True
        📊 Contains:
           • Grids: 17
           • Widgets: 28
           • DynamicGrids: 1
           📁 Referenced Grid Files:
              - $(AppDir)\Header\Grid.Header.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 2
                    • DynamicGrids: 0
              - $(AppDir)\$(DemoDir)\Panel.Message.xml
                 ℹ️  Contains runtime placeholder(s): $(DemoDir)
                    (Will be resolved dynamically at runtime)
              - $(AppDir)\$(DemoDir)\Panel.Message.xml
                 ℹ️  Contains runtime placeholder(s): $(DemoDir)
                    (Will be resolved dynamically at runtime)
              - $(AppDir)\$(DemoDir)\Panel.Message.xml
                 ℹ️  Contains runtime placeholder(s): $(DemoDir)
                    (Will be resolved dynamically at runtime)
              - $(AppDir)\$(DemoDir)\Panel.Message.xml
                 ℹ️  Contains runtime placeholder(s): $(DemoDir)
                    (Will be resolved dynamically at runtime)
           🔄 DynamicGrid Configurations:
              - ID: unknown

  📄 Tab: Tab.Legal
     🔍 Attributes: ID=Tab.Legal, Width=100%g, Height=100%g, hgap=0, vgap=0, Align=NW, TabTitle=Legal, File=$(AppDir)\Tab.Legal.xml, Task=SetTab.$(TabTitle)
     📂 External File: $(AppDir)\Tab.Legal.xml
     📂 Resolved Path: IPU_DEMO\Tab.Legal.xml
     📂 Adjusted Path: Tab.Legal.xml
     📂 Full Path: D:\Intel Vision 2022\Marvin\IPU_DEMO\Tab.Legal.xml
     📂 Exists: True
        📊 Contains:
           • Grids: 9
           • Widgets: 2
           • DynamicGrids: 0
           📁 Referenced Grid Files:
              - $(AppDir)\Header\Grid.Header.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 2
                    • DynamicGrids: 0

  📄 Tab: Tab.Details
     🔍 Attributes: ID=Tab.Details, Width=100%g, Height=100%g, hgap=0, vgap=0, Align=NW, TabTitle=Details, File=$(AppDir)\Tab.Details.xml, Task=SetTab.$(TabTitle)
     📂 External File: $(AppDir)\Tab.Details.xml
     📂 Resolved Path: IPU_DEMO\Tab.Details.xml
     📂 Adjusted Path: Tab.Details.xml
     📂 Full Path: D:\Intel Vision 2022\Marvin\IPU_DEMO\Tab.Details.xml
     📂 Exists: True
        📊 Contains:
           • Grids: 9
           • Widgets: 2
           • DynamicGrids: 0
           📁 Referenced Grid Files:
              - $(AppDir)\Header\Grid.Header.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 2
                    • DynamicGrids: 0

  📄 Tab: Tab.Signage
     🔍 Attributes: ID=Tab.Signage, Width=100%g, Height=100%g, hgap=0, vgap=0, Align=NW, TabTitle=Intel IPU, File=$(AppDir)\Tab.Signage.xml, Task=SetTab.$(TabTitle)
     📂 External File: $(AppDir)\Tab.Signage.xml
     📂 Resolved Path: IPU_DEMO\Tab.Signage.xml
     📂 Adjusted Path: Tab.Signage.xml
     📂 Full Path: D:\Intel Vision 2022\Marvin\IPU_DEMO\Tab.Signage.xml
     📂 Exists: True
        📊 Contains:
           • Grids: 6
           • Widgets: 2
           • DynamicGrids: 0
           📁 Referenced Grid Files:
              - $(AppDir)\Header\Grid.Header.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 2
                    • DynamicGrids: 0

  📄 Tab: Tab.Script
     🔍 Attributes: ID=Tab.Script, Width=100%g, Height=100%g, hgap=0, vgap=0, Align=NW, TabTitle=Intel IPU, File=$(AppDir)\Tab.Script.xml
     📂 External File: $(AppDir)\Tab.Script.xml
     📂 Resolved Path: IPU_DEMO\Tab.Script.xml
     📂 Adjusted Path: Tab.Script.xml
     📂 Full Path: D:\Intel Vision 2022\Marvin\IPU_DEMO\Tab.Script.xml
     📂 Exists: True
        📊 Contains:
           • Grids: 6
           • Widgets: 2
           • DynamicGrids: 0
           📁 Referenced Grid Files:
              - $(AppDir)\Header\Grid.Header.xml
                 📊 Structure:
                    • Nested Grids: 1
                    • Widgets: 2
                    • DynamicGrids: 0

📂 External Files:
  ✓ D:\Intel Vision 2022\Marvin\IPU_DEMO\DefinitionFiles\Alias.List.Global.xml

🔗 Alias Cascade Analysis:

  Alias Dependencies:
    Button.Color = $(Intel_Color5)
      Chain: Intel_Color5 → Button.Color
    GRPC_FAIL_SCALE = MarvinMath($(GRPC_LINE_GRAPH_Y),DIV,$(MAX_VALUE))
      Chain: GRPC_LINE_GRAPH_Y → GRPC_FAIL_SCALE
    GRPC_SUCCESS_SCALE = MarvinMath($(GRPC_LINE_GRAPH_Y),DIV,$(MAX_VALUE))
      Chain: GRPC_LINE_GRAPH_Y → GRPC_SUCCESS_SCALE
    Grid.Base.Height = MarvinMath($(CANVAS_HEIGHT),-,$(ToolBar.Height))
      Chain: CANVAS_HEIGHT → Grid.Base.Height
    Grid.Base.Width = $(CANVAS_WIDTH)
      Chain: CANVAS_WIDTH → Grid.Base.Width
    ImageDir = $(AppDir)/Images
      Chain: AppDir → ImageDir
    Scale.Height = MarvinMath($(CANVAS_HEIGHT),div,900,2)
      Chain: CANVAS_HEIGHT → Scale.Height
    Scale.Width = MarvinMath($(CANVAS_WIDTH),div,1600,2)
      Chain: CANVAS_WIDTH → Scale.Width

📋 Information:
  ℹ️  INFO: File size: 8275 characters
  ℹ️  INFO: Root element: <Marvin>
  ℹ️  INFO: Found 39 alias definition(s)
  ℹ️  INFO: Found 39 alias definition(s)
  ℹ️  INFO: Found 8 Tab definition(s): Tab.Thanks, Tab.Initiator.Generation, Tab.Initiator.IPU, Tab.Initiator.Cloud, Tab.Legal, Tab.Details, Tab.Signage, Tab.Script
  ℹ️  INFO: Found 6 Tab reference(s): Tab.Initiator.Generation, Tab.Initiator.IPU, Tab.Initiator.Cloud, Tab.Signage, Tab.Legal, Tab.Details
  ℹ️  INFO: Loaded 1 external file(s)

⚠️  Warnings:
  ⚠️  WARNING: Defined but not referenced: Tab.Thanks, Tab.Script

======================================================================
✅ VALIDATION PASSED (with warnings)
======================================================================