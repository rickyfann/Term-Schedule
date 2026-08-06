# Term Scheduler
## Table of Contents
1. [What is this?](#what-is-this)
2. [How to use](#how-to-use)
3. [The Tool](#the-tool)

## What is this?
This is a tool that will automatically generate a calendar based on your inputted lessons, days required for each lesson, and will account for holidays / flex days based on the current calendar year.
## How to use
You will need two information groups. Your lesson titles, and school-board specific holidays

Simply provide a text form of your lesson plans in order, similar to the following.

```
Introduction 
Diagnostic Quiz [#aa6767]
Polynomials [3]
Exponentials [2]
Polynomial Quiz + Introduction to Factoring [1]
Factoring by Grouping [2]
Factoring by axc + b [2]
Test
```

Note a couple different features above. Numbers in square brackets such as `[3]` indicate a lesson which spans more than one day. Hex-codes within square brackets such as `[#aa6767]` indicate a custom colour for the specific day. You can choose any colour provided that you know the hex-code for.

The second thing you need is a list of the PD days for your specific board.

I may implement a library of schoolboard days in another iteration.

It should look something like the following.

```
2026-09-10 : PD Day 1
2026-09-14 : PD Day 2
2026-09-16 : PD Day 3
2026-09-21 : Pass
```