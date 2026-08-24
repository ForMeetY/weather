package com.example.weathershow.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * @author X
 * @date 2026/6/9 19:02
 */

/*
* 用于响应结果
* */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Result {
    private Integer code; // 编码 1成功 0失败
    private String msg; // 错误信息
    private Object data; // 数据

    public static Result success() {
        Result result = new Result();
        result.setCode(1);
        result.setMsg("操作成功");
        return result;
    }
    public static Result success(Object data) {
        Result result = new Result();
        result.setCode(1);
        result.setMsg("操作成功");
        result.setData(data);
        return result;
    }
    public static Result error(String msg) {
        Result result = new Result();
        result.setCode(0);
        result.setMsg(msg);
        return result;
    }
    public static Result error() {
        Result result = new Result();
        result.setCode(0);
        result.setMsg("操作失败");
        return result;
    }

}
