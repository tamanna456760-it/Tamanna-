import si from 'systeminformation'

export async function systemMonitor(){

setInterval(async()=>{

const cpu = await si.currentLoad()
const mem = await si.mem()

console.log("CPU:",cpu.currentLoad.toFixed(2))
console.log("RAM:",(mem.used/mem.total*100).toFixed(2)+"%")

},5000)

}