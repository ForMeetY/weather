import request from '@/api/index'

export const getKpi = async () => {
    const res = await request.get('/kpi')
    return res.data
}

// 返回气温趋势图
export const getTrendYear = async () => {
    const res = await request.get('/trendYear')
    return res.data
}

//月度气温趋势图

export const getTrendMonth = async () => {
    const res = await request.get('/trendMonth')
    return res.data
}

// 极端天气
export const getExtremeWeather = async () => {
    const res = await request.get('/extreme')
    return res.data
}

// 季节极端天气的玫瑰图
export const getSeasonalExtremeWeather = async () => {
    const res = await request.get('/extremeSeason')
    return res.data
}

// 年偏差面积组合图
export const getYearlyDeviation = async () => {
    const res = await request.get('/extremeIntensity')
    return res.data
}

// 月偏差面积组合图
export const getMonthlyDeviation = async () => {
    const res = await request.get('/monthlyIntensity')
    return res.data
}

// 日差温度统计分析
export const getDiurnalDeviation = async () => {
    const res = await request.get('/dayDistribution')
    return res.data
}

// 日差季节分布箱线图
export const getSeasonalDeviation = async () => {
    const res = await request.get('/diurnalSeason')
    return res.data
}

// 日差与平均气温散点图
export const getScatterChart = async () => {
    const res = await request.get('/dayDistributionByMonth')
    return res.data
}

// 月度平均日较差（折线图用）
export const getMonthlyDeviationLine = async () => {
    const res = await request.get('/monthDistribution')
    return res.data
}

// 预测数据
export const getPrediction = async () => {
    const res = await request.get('/forecast')
    return res.data
}

// 真实数据2024
export const getActualData = async () => {
    const res = await request.get('/actualData')
    return res.data
}