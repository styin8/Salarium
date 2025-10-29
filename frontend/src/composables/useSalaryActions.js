import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useSalaryStore } from '../store/salary'

export function useSalaryActions() {
  const salaryStore = useSalaryStore()
  const loading = ref(false)
  const dialogVisible = ref(false)

  async function createSalary(personId, payload, options = {}) {
    const { 
      successMessage = '工资记录添加成功',
      closeDialog = true,
    } = options

    loading.value = true
    try {
      const result = await salaryStore.createSalary(personId, payload)
      ElMessage.success(successMessage)
      
      if (closeDialog && dialogVisible.value !== undefined) {
        dialogVisible.value = false
      }
      
      return result
    } catch (error) {
      console.error('创建工资记录失败:', error)
      
      if (error.message === '已有创建操作在进行中') {
        ElMessage.warning(error.message)
      } else if (error.response) {
        ElMessage.error(`创建失败: ${error.response.data.detail || '服务器错误'}`)
      } else {
        ElMessage.error('创建工资记录失败，请检查网络连接')
      }
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updateSalary(salaryId, payload, options = {}) {
    const { 
      successMessage = '工资记录更新成功',
      closeDialog = true,
    } = options

    loading.value = true
    try {
      const result = await salaryStore.updateSalary(salaryId, payload)
      ElMessage.success(successMessage)
      
      if (closeDialog && dialogVisible.value !== undefined) {
        dialogVisible.value = false
      }
      
      return result
    } catch (error) {
      console.error('更新工资记录失败:', error)
      
      if (error.message === '已有更新操作在进行中') {
        ElMessage.warning(error.message)
      } else if (error.response) {
        ElMessage.error(`更新失败: ${error.response.data.detail || '服务器错误'}`)
      } else {
        ElMessage.error('更新工资记录失败，请检查网络连接')
      }
      throw error
    } finally {
      loading.value = false
    }
  }

  async function deleteSalary(salaryId, yearMonth, options = {}) {
    const { 
      confirmMessage = `确定要删除 ${yearMonth} 的工资记录吗？`,
      successMessage = '删除成功',
    } = options

    try {
      await ElMessageBox.confirm(
        confirmMessage,
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
      
      loading.value = true
      await salaryStore.deleteSalary(salaryId)
      ElMessage.success(successMessage)
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除工资记录失败:', error)
        
        if (error.message === '已有删除操作在进行中') {
          ElMessage.warning(error.message)
        } else {
          ElMessage.error('删除失败')
        }
        throw error
      }
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    dialogVisible,
    createSalary,
    updateSalary,
    deleteSalary,
  }
}
