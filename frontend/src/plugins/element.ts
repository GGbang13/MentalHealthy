import type { App, Component } from 'vue'
import {
  ElAlert,
  ElButton,
  ElCard,
  ElDatePicker,
  ElDialog,
  ElDrawer,
  ElEmpty,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElOption,
  ElRadioButton,
  ElRadioGroup,
  ElSelect,
  ElSlider,
  ElSwitch,
  ElTable,
  ElTableColumn,
  ElTag,
  ElTimeline,
  ElTimelineItem
} from 'element-plus'

import 'element-plus/es/components/alert/style/css'
import 'element-plus/es/components/button/style/css'
import 'element-plus/es/components/card/style/css'
import 'element-plus/es/components/date-picker/style/css'
import 'element-plus/es/components/dialog/style/css'
import 'element-plus/es/components/drawer/style/css'
import 'element-plus/es/components/empty/style/css'
import 'element-plus/es/components/form/style/css'
import 'element-plus/es/components/form-item/style/css'
import 'element-plus/es/components/input/style/css'
import 'element-plus/es/components/input-number/style/css'
import 'element-plus/es/components/message/style/css'
import 'element-plus/es/components/option/style/css'
import 'element-plus/es/components/radio-button/style/css'
import 'element-plus/es/components/radio-group/style/css'
import 'element-plus/es/components/select/style/css'
import 'element-plus/es/components/slider/style/css'
import 'element-plus/es/components/switch/style/css'
import 'element-plus/es/components/table/style/css'
import 'element-plus/es/components/table-column/style/css'
import 'element-plus/es/components/tag/style/css'
import 'element-plus/es/components/timeline/style/css'
import 'element-plus/es/components/timeline-item/style/css'

const components: Component[] = [
  ElAlert,
  ElButton,
  ElCard,
  ElDatePicker,
  ElDialog,
  ElDrawer,
  ElEmpty,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElOption,
  ElRadioButton,
  ElRadioGroup,
  ElSelect,
  ElSlider,
  ElSwitch,
  ElTable,
  ElTableColumn,
  ElTag,
  ElTimeline,
  ElTimelineItem
]

export const installElement = (app: App) => {
  components.forEach((component) => {
    if (component.name) {
      app.component(component.name, component)
    }
  })
}
